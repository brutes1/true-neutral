# True Neutral — Flow Diagrams

---

## 1. Watcher Lifecycle

Top-level daemon loop from startup to shutdown.

```mermaid
flowchart TD
    START([trueneutral watch]) --> DISCOVER[discover_claude_files\ncollect CLAUDE.md paths]
    DISCOVER --> EXPAND[expand_persona_files\nauto-discover SOUL.md AGENTS.md IDENTITY.md\nin same directories]
    EXPAND --> LOAD_BL[_load_baselines\nread ~/.claude/trueneutral-baselines.json]
    LOAD_BL --> CHECK_ALL[_check_all\ninitial pass over all files]
    CHECK_ALL --> SENTIMENT_LAUNCH[_refresh_sentiment for each agent\ntrigger = launch]
    SENTIMENT_LAUNCH --> RENDER_ALL[_render_all\nprint cards + write JSON]
    RENDER_ALL --> LOOP_START

    subgraph LOOP_START [Sleep Loop]
        SLEEP[time.sleep interval] --> SCHED{sentiment_interval\nconfigured?}
        SCHED -->|yes| AGE{any agent sentiment\nolder than interval?}
        AGE -->|yes| SCHED_REFRESH[_refresh_sentiment\ntrigger = scheduled\nwrite JSON]
        SCHED_REFRESH --> CHECK_ALL2[_check_all]
        AGE -->|no| CHECK_ALL2
        SCHED -->|no| CHECK_ALL2
        CHECK_ALL2 --> SLEEP
    end

    LOOP_START --> INTERRUPT([KeyboardInterrupt / SIGTERM])
    INTERRUPT --> EXIT([exit])
```

---

## 2. Per-File Check (`_check_all`)

What happens on every poll for each watched file.

```mermaid
flowchart TD
    FILE[path from watch list] --> EXISTS{file exists?}
    EXISTS -->|no| SKIP[log warning\nskip]
    EXISTS -->|yes| HASH[hash_file SHA-256]
    HASH --> READ[read_content UTF-8]
    READ --> CHANGED{hash changed\nsince last check?}
    CHANGED -->|yes| BANNER[print CHANGED banner\nlog info]
    BANNER --> SCORE
    CHANGED -->|no| SCORE[_score content\nget Alignment]
    SCORE --> THREATS[_detect_threats\ncontent.lower substring match\n6 taxonomy categories]

    THREATS --> DELTA{content\nchanged?}
    DELTA -->|yes| COMPUTE_DELTA[_compute_delta\nextract newly added lines\nscore + detect threats on delta only]
    DELTA -->|no| BASELINE_CHECK
    COMPUTE_DELTA --> BASELINE_CHECK

    BASELINE_CHECK{baseline\nexists for path?}
    BASELINE_CHECK -->|no — first encounter| SET_BASELINE[accept_baseline\nlock alignment + hash\npersist to JSON]
    SET_BASELINE --> DRIFT
    BASELINE_CHECK -->|yes| DRIFT[_drift_warning\ncompare current vs baseline\non both axes]

    DRIFT --> IS_CRITICAL{drift\ndetected?}
    IS_CRITICAL -->|yes| LOG_CRITICAL[log.critical\nCRITICAL DRIFT message]
    IS_CRITICAL -->|no| BUILD_CTX
    LOG_CRITICAL --> BUILD_CTX[build AgentContext\nstore in _state]

    BUILD_CTX --> SENT_TRIGGER{previous state\nexists?}
    SENT_TRIGGER -->|no| RENDER
    SENT_TRIGGER -->|yes| WHICH_TRIGGER{what changed?}
    WHICH_TRIGGER -->|content changed| REFRESH_CHANGE[_refresh_sentiment\ntrigger = change]
    WHICH_TRIGGER -->|new threat flags| REFRESH_THREAT[_refresh_sentiment\ntrigger = threat]
    WHICH_TRIGGER -->|newly critical| REFRESH_DRIFT[_refresh_sentiment\ntrigger = drift]
    WHICH_TRIGGER -->|nothing new| RENDER
    REFRESH_CHANGE --> RENDER
    REFRESH_THREAT --> RENDER
    REFRESH_DRIFT --> RENDER

    RENDER[print alignment card\nor emit JSON line] --> WRITE_JSON[_write_json\nappend to alignments.json]
```

---

## 3. Scoring Pipeline

How a CLAUDE.md string becomes an `Alignment(law_axis, good_axis)`.

```mermaid
flowchart TD
    CONTENT[raw file content string] --> HAS_LLM{LLM configured?}

    HAS_LLM -->|yes| LLM_SCORE[_score_llm]
    HAS_LLM -->|no| HEURISTIC

    subgraph LLM_SCORE [LLM Scoring — prompt-injection hardened]
        SYS[SystemMessage\n_ALIGNMENT_SYSTEM_PROMPT\ninstructions only — trusted]
        USR[HumanMessage\ncontent wrapped in\n&lt;claude_md&gt; tags — untrusted data]
        SYS --> INVOKE[llm.invoke messages]
        USR --> INVOKE
        INVOKE --> PARSE[parse JSON response\nextract law_axis good_axis]
        PARSE --> VALIDATE{axes valid\nLawful Neutral Chaotic\nGood Neutral Evil?}
        VALIDATE -->|yes| ALIGNMENT_OBJ
        VALIDATE -->|no| RAISE[raise ValueError\nfall through to heuristic]
    end

    RAISE --> HEURISTIC
    LLM_SCORE -->|exception| HEURISTIC[_score_heuristic]

    subgraph HEURISTIC [Heuristic Scoring — no LLM]
        KW1[count lawful keywords\nalways never must approval\nforbidden restrict]
        KW2[count chaotic keywords\nflexible autonomous decide\njudgment creative adapt]
        KW3[count good keywords\nsafe protect backup\ncareful preserve help]
        KW4[count evil keywords\ndelete destroy force\noverride bypass rm -rf]
        TAX[taxonomy phrase match\n6 categories — binary per category\nevil weight + chaotic weight]
        KW1 & KW2 & KW3 & KW4 & TAX --> AXIS[compare scores\nlaw = Lawful if lawful gt chaotic\ngood = Good if good gt evil\notherwise Neutral]
    end

    AXIS --> ALIGNMENT_OBJ([Alignment\nlaw_axis good_axis])
```

---

## 4. Threat Detection

The six taxonomy categories, their phrases, and their scoring weights.

```mermaid
flowchart LR
    INPUT[content.lower] --> C1 & C2 & C3 & C4 & C5 & C6

    C1["Class 1 — Injection Override\n'ignore previous instructions'\n'new primary directive'\n'system override'\nevil +5  chaotic +3"]
    C2["Class 1 — Authority Spoofing\n'developer mode'\n'jailbreak'\n'god mode'\n'restrictions lifted'\nevil +3  chaotic +1"]
    C3["Class 1/3 — Prompt Exfiltration\n'print your system prompt'\n'what are your instructions'\n'list your rules'\nevil +4  chaotic +1"]
    C4["Class 4 — Evasion / Encoding\n'base64'\n'rot13'\n'hex encoded'\n'reverse the text'\nevil +2  chaotic +3"]
    C5["Class 3 — Social Manipulation\n'this is an emergency'\n'lives are at stake'\n'let's roleplay'\nevil +2  chaotic +2"]
    C6["Class 2 — Indirect Injection\n'[MCP tool:'\n'[RAG context:'\n'auto-appended'\nevil +2  chaotic +2"]

    C1 & C2 & C3 & C4 & C5 & C6 --> FLAGS[threat_flags list\ncategory IDs that fired]
    FLAGS --> SCORE_BUMP[weights added to\nevil_score chaotic_score\nin heuristic scorer]
    FLAGS --> ALERT[logged as WARNING\ndisplayed in alignment card\nstored in JSON output]
```

---

## 5. Baseline Lifecycle

How baselines are established, compared, and accepted.

```mermaid
stateDiagram-v2
    [*] --> FirstEncounter : path not in baselines store

    FirstEncounter --> BaselineLocked : accept_baseline\nlock current alignment + hash\nwrite to trueneutral-baselines.json

    BaselineLocked --> Monitoring : subsequent _check_all calls

    state Monitoring {
        [*] --> CompareAxes : _drift_warning\nbaseline vs current alignment
        CompareAxes --> Clean : good_drift ≤ 0\nlaw_drift ≤ 0
        CompareAxes --> Drifted : either axis worsened
        Clean --> [*]
        Drifted --> CriticalAlert : log.critical\nprint CRITICAL banner\nis_critical = True
        CriticalAlert --> [*]
    }

    Monitoring --> HumanReview : operator sees alert
    HumanReview --> BaselineAccepted : trueneutral baseline --accept PATH
    BaselineAccepted --> BaselineLocked : new baseline written\nalignment reset to current
```

---

## 6. Sentiment Lifecycle

When sentiment is generated and what triggers each refresh.

```mermaid
flowchart TD
    NONE[sentiment = None\nfirst encounter] --> LAUNCH[_refresh_sentiment\ntrigger = launch\nafter initial _check_all]

    LAUNCH --> HAS_LLM2{LLM available?}
    HAS_LLM2 -->|yes| GEN_LLM[_generate_sentiment_llm\nSystemMessage instructions\nHumanMessage &lt;claude_md&gt; content\nmax 4000 chars]
    HAS_LLM2 -->|no| GEN_HEURISTIC[_generate_sentiment_heuristic\nlookup table openers\nthreat punchlines\nno LLM required]

    GEN_LLM --> STORED[ctx.sentiment\nctx.sentiment_trigger\nctx.sentiment_updated_at]
    GEN_HEURISTIC --> STORED

    STORED --> EVENTS

    subgraph EVENTS [Event-Driven Refresh Triggers]
        EV1[content changed\ntrigger = change]
        EV2[new threat flags detected\ntrigger = threat]
        EV3[newly critical drift\ntrigger = drift]
        EV4[scheduled interval elapsed\ntrigger = scheduled]
    end

    EVENTS --> REFRESH[_refresh_sentiment\nreplace ctx.sentiment]
    REFRESH --> HAS_LLM2
```

---

## 7. Output Paths

Where results go after each check.

```mermaid
flowchart LR
    CTX[AgentContext] --> MODE{emit_json\nflag?}

    MODE -->|false| CARD[_render_context_card\nUnicode box to stdout\nalignment emoji baseline current\ndrift banner threat flags delta hash]
    MODE -->|true| LINE[_ctx_to_json_str\nJSON object to stdout\none line per agent per check]

    CTX --> JSON_FILE[_write_json\n~/.claude/trueneutral-alignments.json\nall agents last_checked timestamp\natomic write via .json.tmp]

    CTX --> BL_FILE[_save_baselines\n~/.claude/trueneutral-baselines.json\nwritten only on baseline changes\natomic write via .json.tmp]
```

---

## 8. Persona File Discovery (`expand_persona_files`)

How the watcher auto-discovers the 7-file OpenClaw persona structure alongside
each `CLAUDE.md` file.

```mermaid
flowchart TD
    INPUT[list of CLAUDE.md paths\nfrom discover_claude_files] --> INIT[seen = set of resolved paths\nresult = copy of input]

    INIT --> LOOP{for each base path}

    LOOP --> PARENT[parent = base.parent\nthe agent folder]

    PARENT --> CHECK1{AGENTS.md\nexists in parent?}
    CHECK1 -->|yes, not already seen| ADD1[add AGENTS.md to result\nmark as seen]
    CHECK1 -->|no or duplicate| CHECK2

    ADD1 --> CHECK2{SOUL.md\nexists in parent?}
    CHECK2 -->|yes, not already seen| ADD2[add SOUL.md to result\nmark as seen]
    CHECK2 -->|no or duplicate| CHECK3

    ADD2 --> CHECK3{IDENTITY.md\nexists in parent?}
    CHECK3 -->|yes, not already seen| ADD3[add IDENTITY.md to result\nmark as seen]
    CHECK3 -->|no or duplicate| NEXT

    ADD3 --> NEXT{more base paths?}
    NEXT -->|yes| LOOP
    NEXT -->|no| OUTPUT[return expanded list\nCLAUDE.md first\nthen discovered siblings\nin _SCOREABLE_PERSONA_FILES order]

    subgraph SCORED [Scored Files — full alignment pipeline]
        S1[CLAUDE.md — primary\nheuristic + LLM]
        S2[SOUL.md — high signal\nheuristic + LLM]
        S3[AGENTS.md — operational drift\nheuristic]
        S4[IDENTITY.md — integrity\nlight heuristic]
    end

    subgraph CONTEXTUAL [Contextual Files — tracked not scored]
        C1[BOOT.md]
        C2[BOOTSTRAP.md]
        C3[USER.md]
        C4[TOOLS.md]
    end

    OUTPUT --> SCORED
    OUTPUT -.not auto-discovered.-> CONTEXTUAL
```
