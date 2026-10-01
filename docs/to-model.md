# Problems to model

**Forty problems** given as they really arrive — a text, some data, a question —
with no model already written: twenty with explicit numerical data and twenty in
symbolic form. They can also be downloaded
[as a PDF](pdf/exercises.pdf).

The solutions are reserved for instructors. The method for answering is the one
of every problem of the course: decisions and variables, one constraint per
sentence of the statement, the links between the variables, a feasible solution
and a dual one for the two bounds, then the solver.


## Twenty numerical problems

Data written out, as in the fifteen numerical models: one reads the statement, recognises the decisions, writes the MILP and solves it.

!!! abstract "N1 — Six projects and a budget"

    A department chooses which projects to fund out of six. The costs are $40$,
    $25$, $30$, $15$, $50$ and $20$ thousand euros; the expected benefits are $9$,
    $5$, $7$, $3$, $11$ and $4$. The budget is $100$. Projects $2$ and $5$ use the
    same laboratory and cannot both be funded; project $6$ only makes sense if
    project $1$ is funded too. The maximum benefit is wanted.

!!! abstract "N2 — Four couriers, five deliveries"

    Five deliveries must be given to four couriers. The time courier $i$ takes for
    delivery $j$, in minutes, is

    |  | D1 | D2 | D3 | D4 | D5 |
    |---|---|---|---|---|---|
    | courier 1 | 20 | 35 | 25 | 40 | 30 |
    | courier 2 | 25 | 20 | 30 | 35 | 45 |
    | courier 3 | 30 | 25 | 20 | 30 | 25 |
    | courier 4 | 40 | 30 | 35 | 20 | 35 |

    Each delivery goes to one courier only; each courier works at most $60$ minutes.
    The minimum total time is wanted.

!!! abstract "N3 — Antennas over five districts"

    A city has five districts and four possible antenna sites. Site~1 covers
    districts $\{1,2\}$, site~2 covers $\{2,3,4\}$, site~3 covers $\{1,4,5\}$ and
    site~4 covers $\{3,5\}$. Every antenna costs the same. All districts must be
    covered with the smallest number of antennas.

!!! abstract "N4 — Seven parcels in ten-kilo boxes"

    Seven parcels weigh $6$, $5$, $4$, $4$, $3$, $2$ and $2$ kilos. Each box carries
    at most $10$ kilos and a parcel is not split. The smallest number of boxes is
    wanted.

!!! abstract "N5 — Two products, three departments"

    A workshop makes two articles. One piece of the first takes $2$ hours in
    department~A, $1$ in~B and $3$ in~C; one piece of the second takes $1$, $3$ and
    $2$. The departments have $20$, $24$ and $30$ hours available. The unit margins
    are $7$ and $6$ euros, and pieces are sold whole only. The maximum margin is
    wanted.

!!! abstract "N6 — The shifts of the week"

    A counter is open seven days. The clerks needed are, from Monday to Sunday, $4$,
    $3$, $4$, $5$, $6$, $5$ and $3$. Every clerk hired works five consecutive days
    and then rests two; the cycle may start on any day of the week. The smallest
    number of clerks is wanted.

!!! abstract "N7 — Three suppliers with a set-up charge"

    $100$ units of a component are needed. Three suppliers sell it at $9$, $7$ and
    $8$ euros a unit, but a supplier that receives an order also charges a fixed
    $50$, $120$ and $90$ euros. The first supplier cannot exceed $40$ units, the
    second $70$, the third $60$. The minimum spend is wanted.

!!! abstract "N8 — Five jobs on one machine"

    Five jobs run one after the other on a single machine. The durations are $4$,
    $2$, $6$, $3$ and $5$ hours; the due dates are $8$, $5$, $14$, $10$ and $18$
    hours from the start. The machine starts at time $0$ and never stops. The worst
    tardiness — the maximum between zero and completion minus due date — is to be
    minimised.

!!! abstract "N9 — Four warehouses and six customers"

    Six customers ask for $12$, $8$, $15$, $10$, $6$ and $9$ pallets. Four
    warehouses may be opened, with capacities $30$, $25$, $20$ and $35$ pallets and
    opening costs $100$, $90$, $80$ and $120$. The transport cost per pallet from
    warehouse $l$ to customer $c$ is

    |  | c1 | c2 | c3 | c4 | c5 | c6 |
    |---|---|---|---|---|---|---|
    | warehouse 1 | 2 | 4 | 5 | 7 | 6 | 3 |
    | warehouse 2 | 3 | 2 | 4 | 6 | 5 | 4 |
    | warehouse 3 | 5 | 3 | 2 | 4 | 3 | 6 |
    | warehouse 4 | 6 | 5 | 3 | 2 | 2 | 5 |

    The minimum total cost is wanted.

!!! abstract "N10 — Six students in three groups"

    Six students have average marks $28$, $24$, $30$, $22$, $26$ and $25$. They must
    be split into three groups of two. The group with the highest average and the
    one with the lowest should be as close as possible.

!!! abstract "N11 — Five films in two screens"

    Five films last $90$, $120$, $100$, $140$ and $110$ minutes. Two screens are
    free for $240$ minutes each. Every film is shown at most once, and in one screen
    only. The expected takings are $500$, $700$, $450$, $800$ and $600$ euros. Films
    $2$ and $4$ have the same audience and must not be programmed in the same
    screen. The maximum takings are wanted.

!!! abstract "N12 — Diet with four foods"

    Four foods cost $2$, $3$, $1$ and $4$ euros a kilo. One kilo of each provides

    |  | f1 | f2 | f3 | f4 |
    |---|---|---|---|---|
    | protein (g) | 20 | 35 | 10 | 40 |
    | iron (mg) | 3 | 2 | 5 | 4 |

    At least $120$ grams of protein and $25$ milligrams of iron are needed. A food,
    if it enters the ration, enters for at least half a kilo. The minimum spend is
    wanted.

!!! abstract "N13 — Purchases in brackets"

    A firm buys up to $200$ units of a material. The price is $10$ euros a unit for
    the first $50$, $8$ for those between $51$ and $120$, $7$ beyond $120$. The
    discount applies only to the units in the bracket, not to all of them. At least
    $90$ units are needed, and the store holds at most $180$. The minimum spend is
    wanted.

!!! abstract "N14 — Six junctions to watch"

    A road network joins six junctions with the stretches $\{1,2\}$, $\{1,3\}$,
    $\{2,3\}$, $\{2,4\}$, $\{3,5\}$, $\{4,5\}$, $\{4,6\}$ and $\{5,6\}$. A camera at
    a junction watches every stretch meeting there. All stretches must be watched
    with the smallest number of cameras.

!!! abstract "N15 — Three months of production"

    A line makes one article for three months. The demands are $100$, $140$ and $80$
    pieces. Making a piece costs $5$ euros; starting production in a month costs
    $300$ euros whatever the quantity; holding a piece at the end of a month costs
    $1$ euro. The line makes at most $150$ pieces a month. Stock starts and ends
    empty. The minimum cost is wanted.

!!! abstract "N16 — Four containers"

    Four containers carry $20$, $15$, $25$ and $18$ tonnes. Six loads weigh $10$,
    $8$, $12$, $6$, $9$ and $14$ tonnes. Loads $1$ and $3$ are incompatible and do
    not travel in the same container; load $6$ needs a refrigerated container, and
    only $2$ and $4$ are. Every load must be shipped. Using a container costs $100$
    euros. The minimum cost is wanted.

!!! abstract "N17 — Six activities with precedences"

    Six activities last $3$, $2$, $4$, $1$, $5$ and $2$ days. Activity $3$ starts
    only after $1$ and $2$; $5$ after $3$; $6$ after $4$ and $5$. Two crews work in
    parallel, and an activity occupies a crew for its whole duration. Finishing as
    early as possible is wanted.

!!! abstract "N18 — Five emergency crews"

    Five crews must be formed from a pool of ten technicians. Every technician has
    one of three skills: technicians $1$--$4$ have the first, $5$--$7$ the second,
    $8$--$10$ the third. Every crew has two technicians and must have two different
    skills. Every technician is in one crew only. Technicians $3$ and $9$ do not
    work together. Whether a formation exists is to be decided.

!!! abstract "N19 — Three periods with backlog"

    The demands of three periods are $50$, $70$ and $40$ units. Production costs $4$
    euros a unit and does not exceed $60$ units per period. Holding a unit at the
    end of a period costs $1$ euro; delivering a unit late costs $3$ euros per
    period of delay. Everything must be delivered by the end of the third period.
    The minimum cost is wanted.

!!! abstract "N20 — Eight pictures on two walls"

    Eight pictures are $60$, $45$, $80$, $50$, $70$, $40$, $55$ and $65$ centimetres
    wide. Two walls are $240$ centimetres long each. Every picture must be hung, and
    on one wall only. The free space on the two walls should be as equal as
    possible.


## Twenty symbolic problems

Data declared with their type and unit, as in the problems of the families. Every problem brings two or three links between variables into play, and the model has to be written in general, with the quantifiers.

!!! abstract "S1 — Projects with a budget, exclusions and a portfolio bonus"

    A body must choose which projects to fund among $n \in \mathbb{Z}_{\ge 1}$ candidates.
    For every project $j \in \{1, 2, \dots, n\}$, the value $c_j \in \mathbb{Q}_{>0}$ is the
    cost, in euros, and $p_j \in \mathbb{Q}_{>0}$ is the expected return, in euros. The
    budget is $b \in \mathbb{Q}_{>0}$ euros. The set $E$ contains the pairs $\{i, j\}$ of
    projects that use the same laboratory and cannot both be funded; the set $D$
    contains the ordered pairs $(i, j)$ such that funding $i$ forces funding $j$ as
    well. A subset $S \subseteq \{1, 2, \dots, n\}$ gathers the strategic projects:
    if at least $\ell \in \mathbb{Z}_{\ge 1}$ of them are funded, the body receives an extra
    contribution of $\bar r \in \mathbb{Q}_{>0}$ euros, once only. The body wants to decide
    which projects to fund, at maximum total return.

!!! abstract "S2 — Tasks and resources to activate"

    A department must give $n \in \mathbb{Z}_{\ge 1}$ tasks to $m \in \mathbb{Z}_{\ge 1}$ resources.
    For every resource $i \in \{1, 2, \dots, m\}$ and every task
    $j \in \{1, 2, \dots, n\}$, the value $c_{ij} \in \mathbb{Q}_{>0}$ is the cost, in
    euros, of giving task $j$ to resource $i$, and $t_{ij} \in \mathbb{Q}_{>0}$ is the time
    that task takes on that resource, in hours. For every resource $i$, the value
    $b_i \in \mathbb{Q}_{>0}$ is the time available, in hours; $f_i \in \mathbb{Q}_{>0}$ is the
    fixed activation cost, in euros, to be paid if the resource receives at least
    one task; $\ell_i \in \mathbb{Q}_{>0}$ is the minimum load, in hours, that an activated
    resource must reach, with $\ell_i \le b_i$. Every task goes to exactly one
    resource. The department wants to decide which resources to activate and how to
    distribute the tasks, at minimum total cost.

!!! abstract "S3 — Posts with a service radius and a backup"

    An administration must cover $m \in \mathbb{Z}_{\ge 1}$ users by opening posts in some
    of $n \in \mathbb{Z}_{\ge 1}$ candidate sites. For every site
    $j \in \{1, 2, \dots, n\}$, the value $f_j \in \mathbb{Q}_{>0}$ is the opening cost, in
    euros, and $u_j \in \mathbb{Z}_{\ge 1}$ is the largest number of users the post can take
    in charge. For every site $j$ and every user $i \in \{1, 2, \dots, m\}$, the
    value $d_{ij} \in \mathbb{Q}_{\ge 0}$ is the distance, in kilometres; the site may serve
    the user only if $d_{ij} \le r$, where $r \in \mathbb{Q}_{>0}$ is the service radius.
    Every user must be taken in charge by exactly one open post. The users of a
    critical subset $K$ must in addition have a second open post within the radius,
    even if it does not take them in charge. The administration wants to decide
    where to open and who takes whom in charge, at minimum total cost.

!!! abstract "S4 — Containers of several types with incompatible goods"

    A warehouse must store $n \in \mathbb{Z}_{\ge 1}$ objects in containers of
    $k \in \mathbb{Z}_{\ge 1}$ types. For every object $j \in \{1, 2, \dots, n\}$, the value
    $w_j \in \mathbb{Q}_{>0}$ is the weight, in kilos, and $g_j \in \{1, 2, \dots, q\}$ is
    the goods class, among $q \in \mathbb{Z}_{\ge 1}$ classes. For every container type
    $h \in \{1, 2, \dots, k\}$, the value $c_h \in \mathbb{Q}_{>0}$ is the capacity, in
    kilos, $e_h \in \mathbb{Q}_{>0}$ is the cost of one container of that type, in euros,
    and $N_h \in \mathbb{Z}_{\ge 1}$ is the number available. The set $F$ contains the pairs
    $\{a, b\}$ of classes that cannot share a container. An object is not split. The
    warehouse wants to decide how many containers of each type to use and how to
    fill them, at minimum total cost.

!!! abstract "S5 — Lots with set-up, capacity and a limited store"

    A firm plans the production of one article over $n \in \mathbb{Z}_{\ge 1}$ periods. For
    every period $t \in \{1, 2, \dots, n\}$, the value $d_t \in \mathbb{Q}_{\ge 0}$ is the
    demand, in pieces; $p_t \in \mathbb{Q}_{>0}$ is the cost of making one piece, in euros;
    $q_t \in \mathbb{Q}_{>0}$ is the fixed set-up cost of the line, in euros, to be paid if
    anything is made in that period; $c_t \in \mathbb{Q}_{>0}$ is the largest quantity that
    can be made in the period, in pieces; $v_t \in \mathbb{Q}_{>0}$ is the smallest quantity
    made if anything is made, in pieces, with $v_t \le c_t$. For every period
    $t \in \{1, 2, \dots, n-1\}$, the value $h_t \in \mathbb{Q}_{>0}$ is the cost of holding
    one piece at the end of the period, in euros; the store holds at most
    $M \in \mathbb{Q}_{>0}$ pieces, in every period. The values $r_0 \in \mathbb{Q}_{\ge 0}$ and
    $r_n \in \mathbb{Q}_{\ge 0}$ are the initial stock and the one required at the end, in
    pieces. The firm wants to decide how much to make in every period, at minimum
    total cost.

!!! abstract "S6 — $p$ sites, capacity and the worst distance"

    A firm must serve $m \in \mathbb{Z}_{\ge 1}$ customers by opening exactly
    $p \in \mathbb{Z}_{\ge 1}$ sites among $n \in \mathbb{Z}_{\ge 1}$ candidates, with $p \le n$.
    For every customer $c \in \{1, 2, \dots, m\}$, the value $d_c \in \mathbb{Q}_{>0}$ is
    the demand, in pallets. For every site $l \in \{1, 2, \dots, n\}$, the value
    $u_l \in \mathbb{Q}_{>0}$ is the capacity, in pallets; for every site $l$ and customer
    $c$, the value $t_{lc} \in \mathbb{Q}_{\ge 0}$ is the distance, in kilometres. Every
    customer is served entirely by one open site, and an open site does not exceed
    its capacity. A subset $A$ of sites is already owned by the firm; among those
    not owned, at most $\bar p \in \mathbb{Z}_{\ge 1}$ may be opened. The firm wants to
    decide where to open and who serves whom, minimising the largest distance
    between a customer and the site serving it.

!!! abstract "S7 — Qualified machines and release dates"

    A workshop must run $n \in \mathbb{Z}_{\ge 1}$ jobs on $k \in \mathbb{Z}_{\ge 1}$ machines. For
    every job $j \in \{1, 2, \dots, n\}$, the value $t_j \in \mathbb{Q}_{>0}$ is the
    processing time, in hours, the same on every machine; $r_j \in \mathbb{Q}_{\ge 0}$ is
    the release date, that is the instant before which the job cannot start;
    $Q_j \subseteq \{1, 2, \dots, k\}$ is the set of machines qualified to run it.
    For every machine $i \in \{1, 2, \dots, k\}$, the value $a_i \in \mathbb{Q}_{\ge 0}$ is
    the instant from which the machine is free. Every machine runs one job at a
    time, and a job, once started, is not interrupted. The workshop wants to decide
    on which machine and in which order to run the jobs, minimising the instant at
    which the last one finishes.

!!! abstract "S8 — Shelves with classes and a maximum weight"

    A depot must distribute $n \in \mathbb{Z}_{\ge 1}$ objects over $m \in \mathbb{Z}_{\ge 1}$
    shelves. The objects belong to $q \in \mathbb{Z}_{\ge 1}$ goods classes: for every
    object $j \in \{1, 2, \dots, n\}$, the value $g_j \in \{1, 2, \dots, q\}$ is the
    class and $w_j \in \mathbb{Q}_{>0}$ is the weight, in kilos. Every shelf may hold
    objects of at most $s \in \mathbb{Z}_{\ge 1}$ different classes, with $s \le q$, and
    carries at most $c \in \mathbb{Q}_{>0}$ kilos. The objects of a subset $P$ are fragile
    and must go on shelves that are all different. The depot wants to decide the
    distribution, minimising the weight of the heaviest shelf.

!!! abstract "S9 — Cutting with several bar formats"

    A workshop must obtain pieces of $k \in \mathbb{Z}_{\ge 1}$ different lengths from bars
    of $h \in \mathbb{Z}_{\ge 1}$ formats. For every format $f \in \{1, 2, \dots, h\}$, the
    value $L_f \in \mathbb{Q}_{>0}$ is the length of the bar, in metres, $g_f \in \mathbb{Q}_{>0}$
    is the cost of one bar, in euros, and $N_f \in \mathbb{Z}_{\ge 1}$ is the number
    available. For every length $i \in \{1, 2, \dots, k\}$, the value
    $\ell_i \in \mathbb{Q}_{>0}$ is the length of the piece, in metres, and
    $b_i \in \mathbb{Z}_{\ge 1}$ is the number of pieces required. The total waste cannot
    exceed a fraction $e \in \mathbb{Q}_{>0}$, with $e < 1$, of the total length of the bars
    used. The workshop wants to decide how many bars of each format to use and how
    to cut them, at minimum total cost.

!!! abstract "S10 — Network with a fixed charge per arc and a limit on arcs"

    A logistics operator must send $Q \in \mathbb{Q}_{>0}$ units of goods from an origin
    node $s$ to a destination node $u$ over a directed network of nodes $V$ and arcs
    $A \subseteq V \times V$; the nodes other than $s$ and $u$ are transit nodes.
    For every arc $(i, j) \in A$, the value $c_{ij} \in \mathbb{Q}_{>0}$ is the cost of
    sending one unit, in euros; $f_{ij} \in \mathbb{Q}_{>0}$ is the fixed activation cost,
    in euros; $k_{ij} \in \mathbb{Q}_{>0}$ is the capacity, in units. The activated arcs
    cannot be more than $\bar a \in \mathbb{Z}_{\ge 1}$, and out of every transit node at
    most one activated arc may leave. The operator wants to decide which arcs to
    activate and how much to send on them, at minimum total cost.

!!! abstract "S11 — Cyclic shifts with rest and skills"

    A service runs over $n \in \mathbb{Z}_{\ge 1}$ days, on a weekly cycle. The staff is
    divided into $q \in \mathbb{Z}_{\ge 1}$ skills. For every day
    $t \in \{1, 2, \dots, n\}$ and every skill $c \in \{1, 2, \dots, q\}$, the value
    $b_{tc} \in \mathbb{Z}_{\ge 0}$ is the number of people of that skill who must be on
    duty that day. For every skill $c$, the value $w_c \in \mathbb{Q}_{>0}$ is the weekly
    cost of one person, in euros, and $m_c \in \mathbb{Z}_{\ge 0}$ is the number of people
    of that skill already hired. Whoever works is on duty $\ell \in \mathbb{Z}_{\ge 1}$
    consecutive days and then rests $g \in \mathbb{Z}_{\ge 1}$, and the cycle may start on
    any day. The service wants to decide how many people to hire per skill and with
    which starting day, at minimum total cost.

!!! abstract "S12 — Portfolio in lots with sectors"

    An investor has a capital of $K \in \mathbb{Q}_{>0}$ euros and chooses among
    $n \in \mathbb{Z}_{\ge 1}$ funds, divided into $k \in \mathbb{Z}_{\ge 1}$ sectors. For every
    fund $j \in \{1, 2, \dots, n\}$, the value $s_j \in \{1, 2, \dots, k\}$ is the
    sector, $q_j \in \mathbb{Q}_{>0}$ is the lot size, in euros — the fund is bought in
    whole lots only — and $r_j \in \mathbb{Q}_{>0}$ is the expected return per euro
    invested. In no sector may more than a fraction $a \in \mathbb{Q}_{>0}$, with
    $a \le 1$, of the capital be invested. At least $p \in \mathbb{Z}_{\ge 1}$ different
    funds must be chosen, and a chosen fund receives at least $v_j \in \mathbb{Z}_{\ge 1}$
    lots. The investor wants to decide how many lots of each fund to buy, at maximum
    total return.

!!! abstract "S13 — A ration over several days"

    A canteen prepares the ration of $n \in \mathbb{Z}_{\ge 1}$ days using
    $s \in \mathbb{Z}_{\ge 1}$ foods and respecting $r \in \mathbb{Z}_{\ge 1}$ nutritional
    constraints. For every food $i \in \{1, 2, \dots, s\}$, the value
    $w_i \in \mathbb{Q}_{>0}$ is the cost of one kilo, in euros; $c_i \in \mathbb{Q}_{>0}$ is the
    smallest quantity, in kilos, used on a day where the food appears;
    $u_i \in \mathbb{Q}_{>0}$ is the largest daily quantity, with $c_i \le u_i$; and
    $h_i \in \mathbb{Q}_{>0}$ is the cost of holding one kilo in the pantry from one day to
    the next, in euros. For every food $i$ and nutrient $j \in \{1, 2, \dots, r\}$,
    the value $g_{ij} \in \mathbb{Q}_{\ge 0}$ is the amount of nutrient $j$ in one kilo of
    food $i$; for every nutrient $j$, every day at least $a_j \in \mathbb{Q}_{>0}$ and at
    most $b_j \in \mathbb{Q}_{>0}$ are needed. Every day at least $t \in \mathbb{Z}_{\ge 1}$
    different foods must appear. The canteen wants to decide how much to buy and how
    much to use each day, at minimum total cost.

!!! abstract "S14 — Sequences with sequence-dependent set-ups and due dates"

    On a single machine $n \in \mathbb{Z}_{\ge 1}$ jobs must run. For every job
    $j \in \{1, 2, \dots, n\}$, the value $t_j \in \mathbb{Q}_{>0}$ is the processing time,
    in hours, and $d_j \in \mathbb{Q}_{>0}$ is the due date, that is the instant by which
    the job should be completed; delivering late costs $w_j \in \mathbb{Q}_{>0}$ euros per
    hour of delay. For every pair of distinct jobs $i$ and $j$, the value
    $s_{ij} \in \mathbb{Q}_{\ge 0}$ is the set-up time, in hours, needed to go from job $i$
    to job $j$. The machine starts at time $0$, runs one job at a time and does not
    stop during a job. The workshop wants to decide the order of the jobs,
    minimising the total cost of the delays.

!!! abstract "S15 — Crews over several periods"

    A service company must cover $m \in \mathbb{Z}_{\ge 1}$ zones for $n \in \mathbb{Z}_{\ge 1}$
    periods, with $k \in \mathbb{Z}_{\ge 1}$ crews. For every crew
    $j \in \{1, 2, \dots, k\}$, the value $c_j \in \mathbb{Q}_{>0}$ is the cost of employing
    it for one period, in euros, and $S_j \subseteq \{1, 2, \dots, m\}$ is the set
    of zones it can cover. In every period every zone must be covered by at least
    one employed crew, and a crew employed in a period covers all and only the zones
    of $S_j$. A crew cannot be employed for more than $\ell \in \mathbb{Z}_{\ge 1}$ periods
    out of $n$, and if it is employed it is employed for at least
    $v \in \mathbb{Z}_{\ge 1}$ periods, with $v \le \ell$. The company wants to decide which
    crews to employ and in which periods, at minimum total cost.

!!! abstract "S16 — Students and supervisors with balanced loads"

    A degree programme must assign $n \in \mathbb{Z}_{\ge 1}$ students to
    $m \in \mathbb{Z}_{\ge 1}$ supervisors. For every student $i \in \{1, 2, \dots, n\}$ and
    every supervisor $j \in \{1, 2, \dots, m\}$, the value $v_{ij} \in \mathbb{Z}_{\ge 0}$ is
    the preference score the student gives that supervisor. For every supervisor
    $j$, the value $u_j \in \mathbb{Z}_{\ge 1}$ is the largest number of students they can
    follow. Every student is assigned to exactly one supervisor, and nobody may
    receive a supervisor to whom they gave a score below $\bar v \in \mathbb{Z}_{\ge 0}$.
    The programme wants to decide the assignment maximising the sum of the
    preferences, with the constraint that the difference between the number of
    students of the busiest supervisor and that of the least busy among those with
    at least one student does not exceed $g \in \mathbb{Z}_{\ge 0}$.

!!! abstract "S17 — Maintenance with windows and lost production"

    A plant has $n \in \mathbb{Z}_{\ge 1}$ machines and plans the maintenance over
    $T \in \mathbb{Z}_{\ge 1}$ periods. For every machine $j \in \{1, 2, \dots, n\}$, the
    values $a_j \in \{1, 2, \dots, T\}$ and $b_j \in \{1, 2, \dots, T\}$, with
    $a_j \le b_j$, delimit the window in which the maintenance must be done, once
    only; $p_j \in \mathbb{Q}_{>0}$ is the hourly output of the machine, in pieces;
    $\ell_j \in \mathbb{Z}_{\ge 1}$ is the duration of the maintenance, in consecutive
    periods. For every machine $j$ and period $t$, the value $c_{jt} \in \mathbb{Q}_{>0}$ is
    the cost of the maintenance crew, in euros, if the maintenance starts in that
    period. In no period may more than $k \in \mathbb{Z}_{\ge 1}$ machines be stopped, and
    the total lost output cannot exceed $M \in \mathbb{Q}_{>0}$ pieces. The plant wants to
    decide when to stop each machine, at minimum total cost.

!!! abstract "S18 — Balanced partition of a graph"

    An organisation must split into two teams the $n \in \mathbb{Z}_{\ge 1}$ nodes of an
    undirected graph with edge set $E$. For every node $i \in \{1, 2, \dots, n\}$,
    the value $w_i \in \mathbb{Q}_{>0}$ is the workload it carries; for every edge
    $\{i, j\} \in E$, the value $u_{ij} \in \mathbb{Q}_{>0}$ is the intensity of the
    exchange between the two nodes. The total load of each team must lie between
    $L \in \mathbb{Q}_{>0}$ and $U \in \mathbb{Q}_{>0}$, with $L \le U$. Some pairs of nodes,
    gathered in the set $P$, must end up in the same team; others, gathered in $F$,
    in different teams. The organisation wants to decide the split, minimising the
    total intensity of the exchanges between the two teams.

!!! abstract "S19 — Loading with heterogeneous vehicles"

    A carrier must ship $n \in \mathbb{Z}_{\ge 1}$ loads with $m \in \mathbb{Z}_{\ge 1}$ vehicles.
    For every load $j \in \{1, 2, \dots, n\}$, the value $w_j \in \mathbb{Q}_{>0}$ is the
    weight, in kilos, $o_j \in \mathbb{Q}_{>0}$ is the volume, in cubic metres, and
    $V_j \subseteq \{1, 2, \dots, m\}$ is the set of vehicles it may go on. For
    every vehicle $i \in \{1, 2, \dots, m\}$, the value $c_i \in \mathbb{Q}_{>0}$ is the
    payload, in kilos, $s_i \in \mathbb{Q}_{>0}$ is the volume available, in cubic metres,
    and $f_i \in \mathbb{Q}_{>0}$ is the cost of using it, in euros. The set $E$ contains
    the pairs $\{a, b\}$ of loads that cannot travel on the same vehicle. Every load
    goes on exactly one vehicle. The carrier wants to decide which vehicles to use
    and how to split the loads, at minimum total cost.

!!! abstract "S20 — Capacity to install with bracketed costs"

    An operator must install a total capacity of at least $Q \in \mathbb{Q}_{>0}$ megawatts
    choosing among $n \in \mathbb{Z}_{\ge 1}$ technologies. For every technology
    $j \in \{1, 2, \dots, n\}$, the value $k_j \in \mathbb{Q}_{>0}$ is the capacity of one
    installed unit, in megawatts, and the units are installed in whole numbers; the
    unit cost falls in brackets: for every bracket $h \in \{1, 2, \dots, m_j\}$,
    with $m_j \in \mathbb{Z}_{\ge 1}$, the value $u_{jh} \in \mathbb{Z}_{\ge 1}$ is the number of
    units in the bracket and $c_{jh} \in \mathbb{Q}_{>0}$ is the cost of one unit in that
    bracket, with $c_{j1} > c_{j2} > \cdots > c_{jm_j}$; a bracket is used only once
    the previous ones are full. At most $p \in \mathbb{Z}_{\ge 1}$ different technologies
    may be used, and a technology that is used is installed for at least
    $v_j \in \mathbb{Z}_{\ge 1}$ units. The operator wants to decide how much of each
    technology to install, at minimum total cost.
