# Dream Analyzer Demo

## User Question

> What patterns appear in dreams about hidden rooms?

## Run Settings

- **Chat model:** `qwen3:8b`
- **Embedding model:** `nomic-embed-text`
- **Collection:** `dreams_nomic_embed_text`
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
  "query": "hidden room hallway extra room concealed door behind wall"
}
````

### Tool Call 2: `search_dreams_by_keywords`

Status: `executed`

````json
{
  "query": "hidden room"
}
````

### Tool Call 3: `search_dreams`

Status: `not executed`

````json
{
  "query": "hidden room recurring theme"
}
````

## Dreams Retrieved

### 1. Dream `dream-2026-1-11-0`

- Date: `1/11/2026`
- Returned by tool calls: `1, 2`

````text
DREAM_ID: dream-2026-1-11-0
DATE: 1/11/2026
YEAR: 2026
MONTH: 1
DAY: 11
DATE_PRECISION: day
TAGS: house, recurring, character

--- DREAM TEXT ---

Maya showed up at my house carrying a postcard addressed to me with no stamp. The front showed the green-carpeted hidden room, photographed from the doorway. On the back, in handwriting neither of us recognized, it said YOU KEEP FINDING THE WRONG ENTRANCE. We checked the pantry, cabinets, closet, and bedroom wall, but every previous entrance was gone. Maya suggested looking outside. Around the side of the house we found a narrow path between the foundation and a fence that seemed much longer than the property. At the end was a freestanding door with the same brass knob as the pantry room. It opened into the hidden room, but the room was now enormous and contained doors from many earlier dreams arranged along its walls: the school classroom, the zoo maintenance door, the airport kitchen, the flooded hallway. Maya said it looked less like a room and more like a station. In the center was a desk with a guest book. Several pages contained our names and dates of dreams we had not had yet.
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

### 3. Dream `dream-2024-11-17-0`

- Date: `11/17/2024`
- Returned by tool calls: `1, 2`

````text
DREAM_ID: dream-2024-11-17-0
DATE: 11/17/2024
YEAR: 2024
MONTH: 11
DAY: 17
DATE_PRECISION: day
TAGS: house, water, recurring

--- DREAM TEXT ---

Maya, Lena, and I were in the old house when we heard water running somewhere behind the walls. We searched every bathroom and sink but found nothing. Maya remembered the hidden hallway, so we moved a dresser and found a narrow door where there had never been one before. Behind it, the hallway sloped downward and gradually filled with ankle-deep water. Lena wanted to turn back, but I recognized the green carpet from the first hidden room dream underneath the water and felt like we had finally found the same place again. At the bottom was a bedroom completely submerged except for a pocket of air near the ceiling. We could see furniture, books, and framed photographs drifting below. Maya found a valve labeled MEMORY SUPPLY and joked that turning it off might drain the room. When I touched it, every light in the house went out and the water began rising rapidly. We ran uphill, but the hallway seemed much longer on the way back. Just before we reached the door, I looked behind us and saw someone standing motionless in the flooded bedroom.
````

### 4. Dream `dream-2022-5-15-2`

- Date: `5/15/2022`
- Returned by tool calls: `1`

````text
DREAM_ID: dream-2022-5-15-2
DATE: 5/15/2022
YEAR: 2022
MONTH: 5
DAY: 15
DATE_PRECISION: day
TAGS: house, recurring

--- DREAM TEXT ---

Maya came over because I wanted to show her the staircase inside the kitchen cabinets. At first every cabinet looked normal and I felt stupid for having called her, but when she opened the one above the refrigerator there was a narrow wooden staircase going upward into darkness. We climbed for much longer than should have fit inside the house and came out into a furnished room with yellow wallpaper, a record player, and a window overlooking our own roof. Maya found a stack of photographs showing the room at different ages. In the oldest photograph the wallpaper was blue and there was a little girl standing beside the window. In the newest photograph, taken from behind us, Maya and I were standing exactly where we were now. I wanted to leave immediately. Maya kept examining the picture and said whoever took it must still be in the room. We heard one floorboard creak behind the wall, then the cabinet door downstairs slammed shut.
````

### 5. Dream `dream-2026-8-16-0`

- Date: `8/16/2026`
- Returned by tool calls: `1, 2`

````text
DREAM_ID: dream-2026-8-16-0
DATE: 8/16/2026
YEAR: 2026
MONTH: 8
DAY: 16
DATE_PRECISION: day
TAGS: house, recurring

--- DREAM TEXT ---

Maya, Theo, and Lena came with me because I had decided we were finally going to map the hidden room system instead of just wandering through it. We brought tape, markers, a measuring wheel, and a notebook. The freestanding outside door still led into the enormous central room from January. We labeled it HUB and began checking the surrounding doors one at a time. Some opened into places we recognized: the school theater, the gorilla library, the underwater station, the duplicate office. Others opened onto places none of us remembered. Theo stayed in the hub recording connections while Maya and I walked through a door marked 2018 and unexpectedly came back through one marked BASEMENT. After several trips, Lena noticed the map couldn't be drawn on a flat page because some routes contradicted each other. We tried using arrows and layers, but the notebook kept adding lines by itself. Eventually the lines formed a sentence: STOP MAPPING AND PICK A ROOM. All the doors slammed shut except one. Behind it was an ordinary small bedroom with green carpet and sunlight coming through a normal window. For once, nothing looked wrong. That made all four of us reluctant to enter.
````

### 6. Dream `dream-2023-4-2-0`

- Date: `4/2/2023`
- Returned by tool calls: `1`

````text
DREAM_ID: dream-2023-4-2-0
DATE: 4/2/2023
YEAR: 2023
MONTH: 4
DAY: 2
DATE_PRECISION: day
TAGS: house, family

--- DREAM TEXT ---

Lena was helping my family clean out a house that supposedly belonged to an aunt I had never heard of. The first floor was ordinary, but every bedroom upstairs contained furniture from a different period of my life: my childhood desk, an old dorm chair, a couch that looked like one from a future apartment. Lena treated this as completely normal and started labeling boxes by year. In the last bedroom we found a closet with another door at the back. Behind it was a narrow room full of birthday cards addressed to people in my family, including cards for birthdays that had not happened yet. I found one with my name and a date several years in the future. Lena told me not to open it because doing that would be like reading the end of a book first. I opened it anyway. The inside was blank except for a small floor plan showing a room that did not exist on the house map. When I looked up, the closet had become a hallway leading deeper into the house.
````

### 7. Dream `dream-2026-4-19-0`

- Date: `4/19/2026`
- Returned by tool calls: `1, 2`

````text
DREAM_ID: dream-2026-4-19-0
DATE: 4/19/2026
YEAR: 2026
MONTH: 4
DAY: 19
DATE_PRECISION: day
TAGS: school, anxiety

--- DREAM TEXT ---

Lena and I were taking an oral exam in a classroom that looked like a courtroom. The professor asked each student one question, but the questions were about things that had happened in dreams rather than material from class. The student before me was asked what color the submerged traffic light had been. When it was my turn, the professor asked me to name every entrance to the hidden room. I could remember the pantry, cabinet staircase, bedroom wall, bookcase, and outside door, but I knew there were others. Lena quietly held up six fingers from the audience. I guessed six entrances. The professor asked whether I was sure, then opened a door behind the desk that led directly into the green-carpeted room. He said I had forgotten the most obvious entrance: the classroom. Everyone laughed, and I felt the same intense embarrassment as in ordinary school dreams. Lena told me afterward that she had been holding up six because that was her question number, not the answer.
````

### 8. Dream `dream-2025-5-18-0`

- Date: `5/18/2025`
- Returned by tool calls: `1, 2`

````text
DREAM_ID: dream-2025-5-18-0
DATE: 5/18/2025
YEAR: 2025
MONTH: 5
DAY: 18
DATE_PRECISION: day
TAGS: school, recurring

--- DREAM TEXT ---

Maya and I were back at the same impossible school, this time for a class called Applied Memory. The teacher said our final assignment was to reconstruct a room we had forgotten using only objects we could find in the building. Maya immediately started collecting things that reminded her of childhood, but I couldn't decide what room I was supposed to remember. In the basement I found the green carpet from the hidden pantry room, a lamp from the gorilla library, and the wax-paper schedule from the water-math exam. I realized the school was storing objects from other dreams. Maya helped me carry everything into an empty classroom, where we arranged the objects according to a floor plan I somehow knew. When we finished, a door appeared in the wall. Behind it was the hidden room, but now it contained desks instead of a bed. The teacher congratulated us and said we had passed. I asked what the room actually was, and she said, 'That wasn't part of the assignment.'
````

### 9. Dream `dream-2026-5-20-0`

- Date: `5/20/2026`
- Returned by tool calls: `2`

````text
The hidden room had flooded. The water was perfectly clear, and furniture floated in place as if still arranged on an invisible floor. I swam through a doorway into another dry room where towels were stacked on every chair. A note said the flood is only temporary unless you name it.
````

### 10. Dream `dream-2025-5-5-0`

- Date: `5/5/2025`
- Returned by tool calls: `2`

````text
The hidden hallway opened into a small courtyard this time. The sky above it was dark purple, but I could see daylight under one of the doors. There was a fountain full of keys, and every key had a tag with a room name I did not recognize. I picked one labeled laundry attic and immediately heard someone say not that one.
````

### 11. Dream `dream-2025-9-28-0`

- Date: `9/28/2025`
- Returned by tool calls: `2`

````text
Maya, Theo, and Marcus were with me in an airport where every gate had been replaced by a normal room from somebody's house. Gate 12 was a kitchen, Gate 13 was a bedroom, and Gate 14 was a basement with a washing machine running. Our boarding passes said Gate 0, but there was no Gate 0 on the signs. Maya thought we should look for a hidden room because airports in these dreams never behaved like airports anyway. Theo started opening closets inside each gate, while Marcus tried asking employees for help. Eventually we found a small door behind the refrigerator in Gate 12. It opened onto a jet bridge that went straight down instead of outward. At the bottom was a subway platform with a sign for Gate 0. A train arrived, and the conductor told us it was boarding for the airport. Marcus pointed out that we were already in the airport. The conductor said, 'Not the one you need.' Maya got on immediately, so the rest of us followed.
````

## Final Dream Ranking

The agent combines distinct retrieval rankings with reciprocal-rank fusion (RRF).

| Rank | Dream ID | Date | RRF score | Best source rank | Methods | Source ranks |
|---:|---|---|---:|---:|---|---|
| 1 | dream-2026-1-11-0 | 1/11/2026 | 0.032266 | 1 | semantic, bm25 | call 1: #1 (semantic), call 2: #3 (bm25) |
| 2 | dream-2024-11-17-0 | 11/17/2024 | 0.031258 | 3 | semantic, bm25 | call 1: #3 (semantic), call 2: #5 (bm25) |
| 3 | dream-2025-5-18-0 | 5/18/2025 | 0.030835 | 2 | semantic, bm25 | call 1: #8 (semantic), call 2: #2 (bm25) |
| 4 | dream-2026-8-16-0 | 8/16/2026 | 0.030536 | 5 | semantic, bm25 | call 1: #5 (semantic), call 2: #6 (bm25) |
| 5 | dream-2026-4-19-0 | 4/19/2026 | 0.029851 | 7 | semantic, bm25 | call 1: #7 (semantic), call 2: #7 (bm25) |
| 6 | dream-2026-5-20-0 | 5/20/2026 | 0.016393 | 1 | bm25 | call 2: #1 (bm25) |
| 7 | dream-2024-5-9-0 | 5/9/2024 | 0.016129 | 2 | semantic | call 1: #2 (semantic) |
| 8 | dream-2022-5-15-2 | 5/15/2022 | 0.015625 | 4 | semantic | call 1: #4 (semantic) |
| 9 | dream-2025-5-5-0 | 5/5/2025 | 0.015625 | 4 | bm25 | call 2: #4 (bm25) |
| 10 | dream-2023-4-2-0 | 4/2/2023 | 0.015152 | 6 | semantic | call 1: #6 (semantic) |
| 11 | dream-2025-9-28-0 | 9/28/2025 | 0.014706 | 8 | bm25 | call 2: #8 (bm25) |

## Model Response

| dream_id         | date       | relevant evidence                                                                 | conflict/theme                                                                 |
|------------------|------------|------------------------------------------------------------------------------------|--------------------------------------------------------------------------------|
| dream-2026-1-11-0 | 1/11/2026  | Hidden room with doors from earlier dreams, green carpet, guest book              | Room acts as a station, not just a room                                      |
| dream-2024-11-17-0 | 11/17/2024 | Hidden hallway with water, green carpet, valve labeled MEMORY SUPPLY               | Room is connected to memory, water symbolizes emotional or psychological states |
| dream-2025-5-18-0 | 5/18/2025  | Hidden room with objects from other dreams, door appears after arranging objects   | Room is a repository of memories and experiences                             |
| dream-2026-8-16-0 | 8/16/2026  | Hidden room system with multiple doors, mapping leads to contradictions            | Room system is complex and interconnected, resisting linear understanding     |
| dream-2026-4-19-0 | 4/19/2026  | Hidden room with multiple entrances, classroom as an entrance                     | Room is accessible through various contexts, including waking life            |
| dream-2025-5-5-0  | 5/5/2025   | Hidden hallway with keys labeled for rooms, someone warns against certain choices   | Room system is navigable but with potential consequences                     |
| dream-2024-5-9-0  | 5/9/2024   | Hidden room behind a bookcase, contains objects from neighboring apartments         | Room is a shared space, possibly connected to other dreamers' lives           |
| dream-2022-5-15-2 | 5/15/2022  | Hidden staircase leads to a furnished room with photographs showing past and future | Room contains temporal elements, suggesting it exists outside linear time     |
| dream-2023-4-2-0  | 4/2/2023   | Hidden closet leads to a room with birthday cards for future events                | Room contains future-oriented elements, suggesting it is a space for potential |

**Synthesis:**  
Dreams about hidden rooms often feature interconnected spaces that serve as repositories for memories, experiences, and future possibilities. These rooms are frequently accessed through various means—doors behind walls, bookcases, or even classrooms—and are often described as stations or hubs rather than simple rooms. The rooms contain objects from other dreams, suggesting a shared or collective unconscious space. Water and memory are recurring themes, with some rooms flooding or containing valves labeled "MEMORY SUPPLY." The rooms also appear to exist outside of linear time, with photographs showing past and future events. These dreams often involve a sense of discovery, but also a warning against overexploration, as the rooms resist being fully mapped or understood.
