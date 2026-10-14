# Dream Analyzer Demo

## User Question

> What patterns appear in dreams about hidden rooms?

## Run Settings

- **Chat model:** `gemma4:12b`
- **Embedding model:** `qwen3-embedding`
- **Collection:** `dreams_qwen3_embedding`
- **Chroma path:** `data/chroma_db`
- **Dreams path:** `data/dreams.jsonl`
- **Structured dreams path:** `outputs/structured_dreams/dream_features.jsonl`
- **Character mentions tool:** `disabled (file unavailable)`
- **Characters path:** `data/characters.json`
- **Results per search:** `8`
- **Maximum model characters per dream:** `2500`
- **Maximum tool calls:** `3`
- **Maximum synthesis dreams:** `10`
- **Debug trace:** `False`

## Agent Tool Calls

### Tool Call 1: `search_dreams`

Status: `executed`

````json
{
  "query": "hidden room secret passage concealed door secret space hidden door"
}
````

## Dreams Retrieved

### 1. Dream `dream-2025-9-13-1`

- Date: `9/13/2025`
- Returned by tool calls: `1`

````text
DREAM_ID: dream-2025-9-13-1
DATE: 9/13/2025
YEAR: 2025
MONTH: 9
DAY: 13
DATE_PRECISION: day
TAGS: lost

--- DREAM TEXT ---

Hotel corridor with red carpet
room numbers were decimals
key card worked on every door except mine
inside one room a family was watching my childhood home on TV
````

### 2. Dream `dream-2024-5-9-0`

- Date: `5/9/2024`
- Returned by tool calls: `1`

````text
DREAM_ID: dream-2024-5-9-0
DATE: 5/9/2024
YEAR: 2024
MONTH: 5
DAY: 9
DATE_PRECISION: day
TAGS: house, recurring

--- DREAM TEXT ---

Theo helped me move a bookcase in my apartment and we found a door that had been completely hidden behind it. I was excited rather than scared because I immediately recognized it as one of the impossible rooms from earlier dreams. The door opened into a long carpeted room running behind several neighboring apartments. Each section contained objects that seemed to belong to the people living on the other side of the wall: bicycles, family photos, stacks of mail, children's toys. Theo wanted to leave because it felt like trespassing, but I kept walking until we reached a section containing things from my own apartment, including objects I had lost years ago. There was also a cardboard box labeled THINGS YOU HAVEN'T LOST YET. I opened it and found my keys, phone, wallet, and one shoe. Theo pointed out that all of those items were still in my pockets or on my feet. Then the lights went out section by section behind us, and we had to run back before the darkness reached the door.
````

### 3. Dream `dream-2026-1-3-0`

- Date: `1/3/2026`
- Returned by tool calls: `1`

````text
DREAM_ID: dream-2026-1-3-0
DATE: 1/3/2026
YEAR: 2026
MONTH: 1
DAY: 3
DATE_PRECISION: day
TAGS: recurring, house

--- DREAM TEXT ---

The extra room was missing, but I could see its light under the wall. I tried to pry up the baseboard and found a small mailbox built into the floor. Inside was a postcard showing the room from the inside. The message said wish you were here, except the handwriting looked like mine.
````

### 4. Dream `dream-2024-3-16-0`

- Date: `3/16/2024`
- Returned by tool calls: `1`

````text
DREAM_ID: dream-2024-3-16-0
DATE: 3/16/2024
YEAR: 2024
MONTH: 3
DAY: 16
DATE_PRECISION: day
TAGS: house, recurring

--- DREAM TEXT ---

I found a door behind the washing machine. It opened into a long hallway with carpet like a hotel and walls like a basement. Every few feet there was a framed photograph of the hallway itself, but in each photo a person was standing farther away. I did not see anyone in the real hallway, but the last photo showed someone very close to the camera.
````

### 5. Dream `dream-2022-8-14-1`

- Date: `8/14/2022`
- Returned by tool calls: `1`

````text
DREAM_ID: dream-2022-8-14-1
DATE: 8/14/2022
YEAR: 2022
MONTH: 8
DAY: 14
DATE_PRECISION: day
TAGS: 

--- DREAM TEXT ---

tiny note: red hallway, paper birds, someone laughing behind a vending machine
````

### 6. Dream `dream-2026-6-30-0`

- Date: `6/30/2026`
- Returned by tool calls: `1`

````text
DREAM_ID: dream-2026-6-30-0
DATE: 6/30/2026
YEAR: 2026
MONTH: 6
DAY: 30
DATE_PRECISION: day
TAGS: nightmare, house

--- DREAM TEXT ---

There was a door in the hallway that should not have been there. I knew this immediately. The paint around it was fresh, and the knob was warm. I did not open it, but I could hear a room breathing on the other side. When I backed away, another identical door appeared behind me.
````

### 7. Dream `dream-2026-5-20-0`

- Date: `5/20/2026`
- Returned by tool calls: `1`

````text
DREAM_ID: dream-2026-5-20-0
DATE: 5/20/2026
YEAR: 2026
MONTH: 5
DAY: 20
DATE_PRECISION: day
TAGS: water, recurring

--- DREAM TEXT ---

The hidden room had flooded. The water was perfectly clear, and furniture floated in place as if still arranged on an invisible floor. I swam through a doorway into another dry room where towels were stacked on every chair. A note said the flood is only temporary unless you name it.
````

### 8. Dream `dream-2025-1-9-0`

- Date: `1/9/2025`
- Returned by tool calls: `1`

````text
DREAM_ID: dream-2025-1-9-0
DATE: 1/9/2025
YEAR: 2025
MONTH: 1
DAY: 9
DATE_PRECISION: day
TAGS: recurring, house

--- DREAM TEXT ---

The extra room was bright and clean, almost too clean. It had a desk, a lamp, and a single drawer. In the drawer was a map of the house, but the map included rooms I had not found yet. One was labeled animal room. One was labeled after rain. One was labeled do not use as shortcut.
````

## Final Dream Ranking

The agent combines distinct retrieval rankings with reciprocal-rank fusion (RRF).

| Rank | Dream ID | Date | RRF score | Best source rank | Methods | Source ranks |
|---:|---|---|---:|---:|---|---|
| 1 | dream-2025-9-13-1 | 9/13/2025 | 0.016393 | 1 | semantic | call 1: #1 (semantic) |
| 2 | dream-2024-5-9-0 | 5/9/2024 | 0.016129 | 2 | semantic | call 1: #2 (semantic) |
| 3 | dream-2026-1-3-0 | 1/3/2026 | 0.015873 | 3 | semantic | call 1: #3 (semantic) |
| 4 | dream-2024-3-16-0 | 3/16/2024 | 0.015625 | 4 | semantic | call 1: #4 (semantic) |
| 5 | dream-2022-8-14-1 | 8/14/2022 | 0.015385 | 5 | semantic | call 1: #5 (semantic) |
| 6 | dream-2026-6-30-0 | 6/30/2026 | 0.015152 | 6 | semantic | call 1: #6 (semantic) |
| 7 | dream-2026-5-20-0 | 5/20/2026 | 0.014925 | 7 | semantic | call 1: #7 (semantic) |
| 8 | dream-2025-1-9-0 | 1/9/2025 | 0.014706 | 8 | semantic | call 1: #8 (semantic) |

## Model Response

Based on the dream journal entries, several patterns emerge regarding "hidden rooms" and "secret spaces":

### Evidence of Hidden Rooms

| DREAM_ID | DATE | Relevant Evidence | Conflict/Theme |
| :--- | :--- | :--- | :--- |
| dream-2024-5-9-0 | 5/9/2024 | A door hidden behind a bookcase led to a long carpeted room containing items from neighboring apartments and the dreamer's own lost items. | Discovery of "impossible rooms" and the blurring of boundaries between private spaces. |
| dream-2026-1-3-0 | 1/3/2026 | A hidden room was detected by its light under a wall; a mailbox inside contained a postcard of the room with the dreamer's own handwriting. | Self-reflection and the presence of "hidden" spaces within the home. |
| dream-2024-3-16-0 | 3/16/2024 | A door behind a washing machine led to a hallway where photos showed a person getting closer to the camera in each frame. | Voyeurism and the feeling of being watched in a hidden space. |
| dream-2026-5-20-0 | 5/20/2026 | A hidden room was flooded with clear water; a note stated the flood is only temporary unless it is named. | Environmental hazards and the power of naming/identifying. |
| dream-2025-1-9-0 | 1/9/2025 | An extra room contained a map of the house with rooms labeled with abstract concepts (e.g., "after rain," "animal room"). | Exploration and the existence of "unmapped" territory. |
| dream-2026-6-30-0 | 6/30/2026 | A door that "should not have been there" had a warm knob and was heard "breathing" on the other side. | Eerie, sentient, or organic presence in hidden spaces. |

### Synthesis
Dreams involving hidden rooms frequently feature **spatial anomalies** where the boundaries between private properties are blurred (dream-2024-5-9-0) or where the architecture of a home contains "impossible" or "extra" rooms (dream-2026-1-3-0, dream-2025-1-9-0). These spaces often contain **personal artifacts** (dream-2024-5-9-0), **mysterious messages** (dream-2026-1-3-0, dream-2026-5-20-0), or **uncanny elements** such as breathing sounds (dream-2026-6-30-0) and escalating visual threats (dream-2024-3-16-0). The recurring nature of these dreams suggests a consistent theme of exploring the "hidden" layers of the dreamer's environment.
