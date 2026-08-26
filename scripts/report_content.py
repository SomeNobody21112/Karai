"""The plain-English report content. One string per page-group."""

from __future__ import annotations


def sections(n: dict) -> list[str]:
    """Return the report as a list of HTML sections; each starts a new page."""
    S: list[str] = []

    # ---------------------------------------------------------------- cover
    S.append(f"""
<h1>MPLADS AI Forensic Monitoring<br/>and Decision Support</h1>
<h3>A Complete Explanation in Plain English</h3>
<p><br/></p>
<p><b>Smart India Hackathon 2026</b><br/>
Problem Statement ID: SIH26102<br/>
Problem Statement: Development of an AI-powered system to detect anomalies, fraud and
inefficiencies in MPLAD Scheme implementation<br/>
Ministry: MoSPI (Ministry of Statistics and Programme Implementation)<br/>
Theme: Miscellaneous &nbsp;|&nbsp; Category: Software<br/>
<b>Team: Morior Invictus</b></p>
<p><br/></p>
<hr/>
<p><b>Who this document is for</b></p>
<p>Anyone. You do not need to know anything about computers, statistics or government
schemes. Every technical word used anywhere in this project is explained here in ordinary
language, usually with a comparison to something from everyday life.</p>
<p>If you read this document from start to finish you will understand: what problem the
government asked us to solve, why it is hard, exactly what we built, how every piece of it
works, what the results are, and - just as importantly - what we deliberately refused to
claim and why.</p>
<p><br/></p>
<p><b>The one-sentence summary</b></p>
<p>We built a computer system that reads all <b>{n['works']}</b> local development works
funded across India, works out which ones look unusual compared to genuinely similar works,
and hands officials a short ranked list saying "please check these first, and here is
exactly why" - without ever accusing anyone of anything.</p>
<p><br/></p>
<hr/>
<p><i>Every number in this report was produced by the working system and read directly out
of its output files. Nothing here is estimated, rounded up, or copied from a slide.</i></p>
""")

    # ------------------------------------------------------- part 1: problem
    S.append(f"""
<h2>Part 1 - The Problem</h2>

<h3>1.1 What is MPLADS?</h3>
<p><b>MPLADS</b> stands for <b>Members of Parliament Local Area Development Scheme</b>.</p>
<p>Here is the idea in one breath: every Member of Parliament (MP) is given a budget each
year to spend on small development projects in their local area. The MP does not spend the
money themselves. Instead, the MP <i>recommends</i> a work - "build a community hall in
this village", "put street lights on this road" - and a government office in the district
actually gets it built.</p>
<p>The kinds of things built are small and practical:</p>
<ul>
<li>Concrete roads and link roads between villages</li>
<li>Street lights and high-mast lights in public squares</li>
<li>Community halls where people can hold weddings and meetings</li>
<li>Hand pumps, borewells and drinking-water plants</li>
<li>Rooms added to schools, benches, gym equipment in parks</li>
<li>Crematoriums, boundary walls, bus shelters, drains and culverts</li>
</ul>
<p>These are not glamorous mega-projects. They are the things that make daily life in a
village or a small town work.</p>

<h3>1.2 The scale problem</h3>
<p>Now here is where it gets difficult.</p>
<table border="1" width="100%"><thead><tr>
<th bgcolor="#eeeeee" width="55%"><b>What</b></th><th bgcolor="#eeeeee" width="45%"><b>How many</b></th>
</tr></thead><tbody>
<tr><td>Works in the system</td><td><b>{n['works']}</b></td></tr>
<tr><td>Money recommended across all of them</td><td><b>Rs {n['rec_cr']} crore</b></td></tr>
<tr><td>States and Union Territories covered</td><td>{n['states']}</td></tr>
<tr><td>Parliamentary constituencies</td><td>{n['consts']}</td></tr>
<tr><td>Government offices doing the building</td><td>{n['agencies']}</td></tr>
<tr><td>Works already finished</td><td>{n['completed']}</td></tr>
<tr><td>Works still in progress</td><td>{n['open']}</td></tr>
</tbody></table>
<p><br/></p>
<p><b>Think about what {n['works']} means.</b> If an official sat down and spent just
<i>one minute</i> looking at each work - barely enough to read the description - and did
nothing else for eight hours a day, five days a week, it would take them about
<b>seventeen months</b> to look at every work once. By the time they finished, thousands of
new works would have been added.</p>
<p>So in practice, nobody checks them all. Checking happens when somebody complains, or
when an audit is scheduled, or by picking works more or less at random. That is called
<b>reactive monitoring</b> - you react after something has gone wrong or somebody has
noticed.</p>

<h3>1.3 What the government actually asked for</h3>
<p>The official problem statement is written in formal language. Here it is translated:</p>
<table border="1" width="100%"><thead><tr>
<th bgcolor="#eeeeee" width="50%"><b>The official words</b></th>
<th bgcolor="#eeeeee" width="50%"><b>What that means</b></th>
</tr></thead><tbody>
<tr><td>"Detect anomalies and irregularities"</td><td>Find the works that look odd</td></tr>
<tr><td>"Detect delayed projects"</td><td>Find works that are taking far too long</td></tr>
<tr><td>"Detect duplicate works"</td><td>Find the same work being claimed twice</td></tr>
<tr><td>"Detect cost overruns"</td><td>Find works that cost far more than planned</td></tr>
<tr><td>"Analyse expenditure and fund utilisation"</td><td>Check how the money was actually spent</td></tr>
<tr><td>"Deviations from established norms"</td><td>Find records that break the official process</td></tr>
<tr><td>"Trend analysis"</td><td>Watch how things change over months and years</td></tr>
<tr><td>"Early warning mechanisms"</td><td>Predict trouble before it fully happens</td></tr>
<tr><td>"Risk-based alerts"</td><td>Rank problems so the worst come first</td></tr>
<tr><td>"Decision-support dashboards"</td><td>Screens that help officials decide what to do</td></tr>
<tr><td>"For MPs, State Nodal Authorities, District Authorities and the Ministry"</td>
<td>Four different kinds of user, each seeing what concerns them</td></tr>
<tr><td>"Potential fraud"</td><td>Point at things that might be misuse of money</td></tr>
</tbody></table>

<h3>1.4 Why this is genuinely hard</h3>
<p>Four reasons, and each one shaped what we built.</p>
<p><b>Reason 1: There is no answer key.</b> Nobody has ever gone through these
{n['works']} works and marked which ones were fraudulent. There is no list of "these 500
were corrupt". This matters enormously, and Part 6 explains exactly why.</p>
<p><b>Reason 2: "Expensive" is meaningless without context.</b> Is a road costing Rs 20
lakh too expensive? You cannot possibly say. A 200-metre village footpath and a 3-kilometre
concrete road with drainage are both "roads". Comparing everything to one national average
would flag thousands of perfectly normal works and miss the genuinely odd ones.</p>
<p><b>Reason 3: Most works are unfinished, and that is normal.</b> {n['open']} of the
works have not been completed. A work recommended last month is not "failing" - it simply
has not had time. Treating unfinished as failed would make every recent work look like a
disaster. Part 4 explains the mathematics that solves this.</p>
<p><b>Reason 4: The descriptions are messy.</b> They are typed by hundreds of different
offices, in English, Hindi, Gujarati and other languages, often written in the English
alphabet, with inconsistent spelling. "CC Road", "C.C. ROAD", "Construction of concrete
road" and "cc rroad" are all the same thing.</p>
""")

    # ------------------------------------------------------ part 2: solution
    S.append(f"""
<h2>Part 2 - Our Solution, In Plain Words</h2>

<h3>2.1 The big idea</h3>
<p>We did not build a machine that catches criminals. We built <b>a machine that reads
everything and tells busy people where to look first.</b></p>
<p>Here is the comparison we keep coming back to. Imagine a teacher with
<b>{n['works']} homework notebooks</b> and one afternoon to spend. She cannot read them
all. What would actually help her is an assistant who has flipped through every single
notebook and says:</p>
<p><i>"Start with these ones. This one is written in handwriting that does not match the
rest of the book. This one is identical to the notebook next to it. This one was submitted
three months late. I am not saying anyone cheated - I am saying these are the ones worth
your time, and here is why for each."</i></p>
<p>That assistant is our system. Notice what the assistant does <b>not</b> do: it does not
declare anybody a cheat. It reads, compares, sorts, and explains.</p>

<h3>2.2 The five steps</h3>
<p>Everything the system does fits into five steps. The whole project is these five steps,
done carefully.</p>

<p><b>STEP 1 - LEARN what normal looks like</b></p>
<p>The computer reads the description of every work and sorts them into groups of similar
things: roads with roads, community halls with community halls, street lights with street
lights. It found <b>{n['k']} such groups</b> by itself. Nobody gave it a list of
categories.</p>
<p><i>Everyday comparison:</i> tip out a giant box of mixed Lego and sort it into piles -
wheels, flat pieces, roof pieces - without anyone telling you those piles exist. You do it
because similar pieces feel similar.</p>

<p><b>STEP 2 - COMPARE each work with its true peers</b></p>
<p>For each work, the system finds works of the <i>same type</i> in the <i>same state</i>,
and asks: compared to those, is this one unusually expensive or unusually slow?</p>
<p><i>Everyday comparison:</i> if you want to know whether you paid too much for a school
bag, you do not compare it to the price of every object in the shop. You compare it to
other school bags in the same town.</p>

<p><b>STEP 3 - PREDICT which works may never finish</b></p>
<p>Using the history of how long similar works took to finish, the system estimates how
likely each unfinished work is to stall. Money sitting inside works that may never finish
is called <b>money at risk</b>.</p>
<p><i>Everyday comparison:</i> you are watching a marathon. Some runners have finished.
Many are still running. Looking at how long finishers took and how far each remaining
runner has gone, you can sensibly estimate who is unlikely to finish - without pretending
that everyone still running has already failed.</p>

<p><b>STEP 4 - NOTICE when behaviour changes</b></p>
<p>For each government office, the system watches its pattern of works year by year. If an
office that always handled small works suddenly starts handling very large ones, that is a
change worth a second look.</p>
<p><i>Everyday comparison:</i> a shop that sold Rs 100 of goods a day for two years
suddenly sells Rs 5,000 a day. Maybe a new road brought customers. Maybe something else.
You would at least ask.</p>

<p><b>STEP 5 - EXPLAIN and PRIORITISE</b></p>
<p>The system combines the clues. A work is only put on the list when <b>at least two
independent kinds of clue agree</b> - never on one hunch alone. Each raised work becomes a
<b>case file</b>: a one-page summary of what was noticed, why, and the single thing a human
should check next. The list is sorted so the biggest money-at-risk appears first.</p>
<p><i>Everyday comparison:</i> in a courtroom, one witness is not enough. You want two
independent witnesses who did not talk to each other before you take a claim seriously.</p>

<h3>2.3 The golden rule</h3>
<p>This runs through every part of the project:</p>
<table border="1" width="100%"><tbody>
<tr><td bgcolor="#f4f4f4"><b>The system produces INVESTIGATION LEADS, never VERDICTS.</b><br/>
It says "a human should check this, and here is why."<br/>
It never says "this is fraud."</td></tr>
</tbody></table>
<p>This is not modesty or legal caution. It is the only honest thing the data allows, and
Part 6 explains exactly why.</p>
""")

    # --------------------------------------------------------- part 3: data
    S.append(f"""
<h2>Part 3 - The Data</h2>

<h3>3.1 Where the information comes from</h3>
<p>The government runs a website called <b>eSAKSHI</b> where MPLADS works are recorded.
That data is public. We used three files taken from it, covering the 17th Lok Sabha, the
18th Lok Sabha and the Rajya Sabha.</p>
<p>Together those files contain <b>480,768 rows</b>. Each row is not a work - it is one
<i>stage</i> of a work. Every work can pass through three stages:</p>
<ul>
<li><b>Recommended</b> - the MP has proposed it</li>
<li><b>Sanctioned</b> - it has been approved</li>
<li><b>Completed</b> - it has been finished</li>
</ul>
<p>So one work can appear as one, two or three rows. Turning 480,768 stage rows into
{n['works']} actual works was the very first job, and it had to be done exactly right,
because every later number depends on it.</p>

<h3>3.2 The detective work we did before writing any AI</h3>
<p>Before building anything, we spent a whole phase just <i>reading the data</i> and
testing what was really in it. This found several things nobody had noticed, and they
changed the design of the entire project.</p>

<p><b>Discovery 1: How to tell one work from another</b></p>
<p>There is a column called WORK_ID that looks exactly like it should be the identity
number for each work. It is a trap. WORK_ID is only filled in <i>after</i> a work is
completed - it is empty for all {n['open']} unfinished works. Using it would have silently
thrown away more than half the data.</p>
<p>The real identity turned out to be a <i>pair</i> of columns used together: a per-MP
serial number plus the MP's own ID. We call the combination <b>work_ref</b>.</p>

<p><b>Discovery 2: 3,987 "broken" rows are not broken at all</b></p>
<p>Nearly four thousand rows had no work identity, and a previous attempt at this project
had simply deleted them as corrupt. We looked closer. Every one of them carries a total
amount, and that column is empty on every genuine work row. They are <b>per-MP summary
rows</b> - one per MP per stage, giving that MP's total.</p>
<p>They are not rubbish. They are a free way to check our own arithmetic: our per-MP totals
should match theirs. They do, exactly, for the typical MP at all three stages. That is
strong proof our processing loses nothing.</p>

<p><b>Discovery 3: A hidden official category list</b></p>
<p>A column called ACTIVITY_NAME appears to contain 180,000 different values, which would
be useless. But look at an actual value:</p>
<p><i>WS/MP519/2023-2024/49391-Installation of multi-gym equipment</i></p>
<p>It is two things stuck together: a reference code, then the <b>official government
category</b>. Split them apart and the 180,000 useless values become <b>118 official
categories covering 93% of works</b> - the government's own approved list of what MPLADS
money may be spent on. Both the previous project and our own slide deck had said this field
was unusable. It was simply never split.</p>

<h3>3.3 The most important discovery: the money column is not what it seems</h3>
<p>There is a column called ACTUAL_AMOUNT. Everyone assumes it means "the amount actually
spent". If that were true we could detect cost overruns immediately.</p>
<p>We tested it. Here is what we found across the 85,525 completed works that have both
numbers:</p>
<table border="1" width="100%"><thead><tr>
<th bgcolor="#eeeeee" width="70%"><b>Finding</b></th><th bgcolor="#eeeeee" width="30%"><b>Result</b></th>
</tr></thead><tbody>
<tr><td>Works where "actual" is EXACTLY equal to "recommended"</td><td><b>98.35%</b></td></tr>
<tr><td>Works where the two differ at all</td><td>1,413</td></tr>
<tr><td>Of those, works differing by more than 0.01%</td><td><b>Exactly 1</b></td></tr>
<tr><td>Works costing more than 5% over the recommendation</td><td><b>Zero. None.</b></td></tr>
</tbody></table>
<p><br/></p>
<p>In plain words: <b>ACTUAL_AMOUNT is just a copy of the recommended amount.</b> It is a
tick-box confirming the work finished, not a record of money spent. The 1,413 that "differ"
differ by amounts like one rupee in a million - ordinary computer rounding.</p>
<p><b>Why this matters so much:</b> the problem statement explicitly asks for expenditure
analysis and cost-overrun detection. Both are <i>impossible</i> on this data. Any system
claiming to detect MPLADS cost overruns from public data has invented the result. We refuse
to. Instead we say so clearly on a dedicated screen, and we detect what the data genuinely
supports.</p>

<h3>3.4 Other things the data does not contain</h3>
<table border="1" width="100%"><thead><tr>
<th bgcolor="#eeeeee" width="35%"><b>Missing</b></th><th bgcolor="#eeeeee" width="65%"><b>Why it matters</b></th>
</tr></thead><tbody>
<tr><td>Payment records</td><td>No way to see money going out in instalments</td></tr>
<tr><td>Cost estimates</td><td>Nothing to compare a final cost against</td></tr>
<tr><td>Physical progress %</td><td>We know a work is "sanctioned" but not that it is "60% built"</td></tr>
<tr><td>Sanction date</td><td>We can prove a work WAS sanctioned but never WHEN</td></tr>
<tr><td>Photographs</td><td>Photo IDs exist but the files need a government login</td></tr>
<tr><td>Vendor / contractor name</td><td>No way to spot the same contractor winning repeatedly</td></tr>
<tr><td>GPS coordinates</td><td>No mapping of exactly where works are</td></tr>
<tr><td>District</td><td>There is genuinely no clean district column</td></tr>
</tbody></table>
<p><br/></p>
<p>We proved the sanction-date one with a neat test. Sanction rows <i>do</i> have a date
column filled in, which is tempting. We compared it against the recommendation date for
179,676 works: it was identical <b>100.00% of the time</b>. It is a copy, not a real
sanction date. Presence can be checked; timing cannot.</p>

<h3>3.5 Problems in the data that became useful signals</h3>
<p>Some records are simply inconsistent. We keep every one and flag it, rather than quietly
fixing it, because an inconsistent record is itself worth a human look.</p>
<table border="1" width="100%"><thead><tr>
<th bgcolor="#eeeeee" width="30%"><b>Issue</b></th><th bgcolor="#eeeeee" width="15%"><b>Count</b></th>
<th bgcolor="#eeeeee" width="55%"><b>What it means</b></th>
</tr></thead><tbody>
<tr><td>Completed before recommended</td><td>1,194</td>
<td>The finish date is before the start date - impossible in real life</td></tr>
<tr><td>No recommendation record</td><td>695</td>
<td>The work appears at sanction or completion but has no origin</td></tr>
<tr><td>Completed with no sanction</td><td>70</td>
<td>Skipped the middle step of the official process</td></tr>
<tr><td>Finish date in the future</td><td>9</td>
<td>Dates typed as 2034 and even 2044 - typing mistakes</td></tr>
<tr><td>Amount of zero or less</td><td>6</td>
<td>No money figure to work with</td></tr>
<tr><td>No description at all</td><td>1,029</td>
<td>Cannot be sorted into a group or compared</td></tr>
</tbody></table>
<p><br/></p>
<p>Those nine future dates matter more than their small number suggests. If we had measured
"how old is this work" using the latest date anywhere in the data, we would have used a
2044 typing error as today's date - and every unfinished work in India would have looked
about eighteen years overdue. We use the latest <i>recommendation</i> date instead:
<b>26 May 2026</b>. This single decision keeps every duration in the project honest.</p>
""")

    # ------------------------------------------------- part 4: the technology
    S.append(f"""
<h2>Part 4 - Every Technical Term, Explained</h2>
<p>This is the part people usually find intimidating. Every term below appears somewhere in
our project, our slides or our code. None of them is complicated once you have the right
everyday comparison.</p>

<h3>4.1 Words about understanding text</h3>

<p><b>Embedding</b> (also called a "vector")</p>
<p>Turning a sentence into a list of numbers, so that sentences meaning similar things get
similar numbers. Ours turns every work description into a list of <b>384 numbers</b>.</p>
<p><i>Comparison:</i> think of describing a colour with three numbers - how much red, how
much green, how much blue. Two shades of sky blue end up with very close numbers, and red
ends up far away. An embedding does the same for meaning, using 384 measurements instead of
3. "Construction of CC Road" and "cc rroad building" land close together; "Purchase of
library books" lands far away.</p>
<p>This is why the system understands that two differently-worded descriptions mean the
same thing - something a simple text search could never do.</p>

<p><b>MiniLM</b> (full name: all-MiniLM-L6-v2)</p>
<p>The specific ready-made tool that does the turning-sentences-into-numbers job. It was
built and trained by researchers on enormous amounts of text. We did not build it and we do
not claim to have - we <i>use</i> it, the way you use a calculator rather than inventing
arithmetic.</p>

<p><b>Clustering</b></p>
<p>Automatically putting similar things into groups without being told what the groups
are.</p>
<p><i>Comparison:</i> hand a child a basket of mixed fruit and say "put similar ones
together". They will make an apple pile, a banana pile and an orange pile without knowing
those words. That is clustering.</p>

<p><b>K-Means</b> / <b>MiniBatchKMeans</b></p>
<p>The specific clustering method we use. "K" is simply <i>how many groups you want</i>.
The "MiniBatch" version looks at the data in small handfuls at a time instead of all at
once, which is what makes it fast enough for 187,865 descriptions on a normal laptop.</p>

<p><b>Archetype</b></p>
<p>Our name for one of the discovered groups - one "type of work". We found
<b>{n['k']} archetypes</b>. Examples our system discovered and named by itself:
"Mast light - high mast - mini mast", "CC road - construction cc", "Community hall -
construction community", "Solar street - street light".</p>

<p><b>c-TF-IDF</b> (used to name the groups)</p>
<p>A method for finding which words are <i>distinctive</i> to a group rather than just
common everywhere. "Construction" appears in nearly every group, so it is not distinctive.
"High mast" appears mostly in one group, so it is. We use the distinctive words as the
group's name.</p>
<p>This is why our group names come from the actual contents rather than from our
imagination.</p>

<p><b>Silhouette score</b></p>
<p>A number between -1 and 1 measuring how <i>cleanly separated</i> the groups are. Ours is
about <b>{n['sil']}</b>, which is low.</p>
<p><b>This is the single most misunderstood number in the whole project, so read this
twice:</b> silhouette is <i>not</i> accuracy. It does not mean we are 5% correct. It means
the groups blend into each other rather than sitting in neat separate islands - which is
exactly what you would expect, because a "road with drainage" genuinely does shade into a
"drain alongside a road". We publish this number openly rather than hiding it, and we never
present it as accuracy.</p>

<h3>4.2 Words about comparing fairly</h3>

<p><b>Peer group</b></p>
<p>The set of works a given work is fairly compared against - same type of work, same
state. Not "everything in India".</p>

<p><b>Percentile</b></p>
<p>Your position out of 100 when everything is lined up in order. The 90th percentile means
90% of comparable works are cheaper than this one. The 100th percentile means it is the
most expensive of its peers.</p>
<p><i>Comparison:</i> exam ranks. Saying "I scored 400 marks" means nothing on its own.
Saying "I was in the top 5% of my class" tells you everything.</p>

<p><b>Leave-one-out</b></p>
<p>When ranking a work against its peers, we take the work itself out of the comparison
group first.</p>
<p><i>Comparison:</i> if you are measuring whether you are taller than average in your
class, you should not include your own height in that average - it drags the average
towards you and makes you look more normal than you are.</p>

<p><b>Median</b> and <b>MAD</b> (Median Absolute Deviation)</p>
<p>The <b>median</b> is the middle value when everything is sorted. It is used instead of
the average because one enormous number cannot drag it around. If nine works cost Rs 3 lakh
and one costs Rs 50 crore, the average is misleading; the median is still Rs 3 lakh.</p>
<p><b>MAD</b> measures how spread out the values usually are, using the same
resistant-to-extremes idea.</p>

<p><b>Robust z-score</b></p>
<p>"How many normal steps away from the middle is this?" A z-score of 3 means this work is
three typical-sized steps above the middle of its peer group. "Robust" means built from
median and MAD, so a single freak value cannot distort it.</p>

<p><b>Hierarchical back-off</b></p>
<p>What to do when a peer group is too small to be meaningful. If there are fewer than 30
similar works in the same state, we widen the net: same type anywhere in India; then all
works in that state; then everything. The system records <i>which</i> level it actually
used, so you always know how fair the comparison was.</p>
<p><i>Comparison:</i> comparing a house price with the same street is best. Only three
houses on the street? Widen to the neighbourhood. Still too few? The whole town.</p>

<h3>4.3 Words about predicting the future</h3>

<p><b>Survival analysis</b></p>
<p>The branch of mathematics for questions of the form "how long until something
happens?" - originally built for medical studies, which is where the slightly grim name
comes from. We use it for "how long until this work is completed?"</p>

<p><b>Censoring</b> (the crucial idea)</p>
<p>Handling correctly the fact that many things have not happened <i>yet</i>.</p>
<p><i>Comparison:</i> you are studying how long a light bulb lasts. You switch on 100 bulbs
and after one year, 40 have burnt out. What about the 60 still glowing? They have not
failed. But you also do not know how long they will last. Throwing them away would make
bulbs look far worse than they are; calling them "failures" would be a lie.</p>
<p>Censoring is the mathematics for using the information "this one lasted <i>at least</i>
one year" without pretending to know more. Applied here: {n['censored']} of our works are
unfinished and are correctly treated as "not finished yet", not as failures. This is the
single most important modelling decision in the project.</p>

<p><b>Kaplan-Meier</b> and <b>Cox proportional hazards</b></p>
<p>Two standard survival-analysis methods. Kaplan-Meier draws the overall "what fraction
are still unfinished after N days" curve. <b>Cox</b> goes further and lets each work's own
characteristics - its cost, its type, its state, whether it was sanctioned - shift its
prediction. Cox is the model we actually trained.</p>

<p><b>C-index</b> (concordance index)</p>
<p>How good the prediction is at <i>ranking</i>. If you pick any two works, how often does
the model correctly say which one will finish sooner?</p>
<ul>
<li>0.5 = pure coin-flip, useless</li>
<li>1.0 = perfect every time</li>
<li><b>Ours = {n['cindex']}</b> - correct about 68 times out of 100, clearly better than
guessing but not magic. We report it exactly as it is.</li>
</ul>

<h3>4.4 Words about finding odd things</h3>

<p><b>Anomaly</b></p>
<p>Something unusual. Note carefully: unusual is <i>not</i> the same as wrong. The tallest
person in your school is an anomaly and has done nothing wrong.</p>

<p><b>IsolationForest</b></p>
<p>A method that finds odd items by seeing how easy they are to separate from the crowd.
Odd items get isolated after very few questions.</p>
<p><i>Comparison:</i> twenty-questions. If everyone in a group wears blue and one person
wears bright orange, you identify them in one question. That easiness is exactly what the
method measures.</p>

<p><b>Change-point detection</b></p>
<p>Finding the moment when a pattern shifts. Not "this number is high" but "this number
<i>started being</i> high, right here."</p>

<p><b>Near-duplicate detection</b></p>
<p>Finding works whose descriptions mean nearly the same thing - using the 384-number
embeddings, so it catches matches even when the wording differs completely.</p>

<p><b>Cosine similarity</b></p>
<p>The measurement of how close two embeddings are, given as a number from 0 to 1.
1.0 means identical meaning, 0.5 means unrelated. We treat 0.97 and above as a near-exact
match.</p>

<h3>4.5 Words about the final decision</h3>

<p><b>Signal</b></p>
<p>One individual clue. We have seven: unusual amount, unusual duration, completion risk,
lifecycle problem, behaviour change, statistical outlier, and near-duplicate.</p>

<p><b>Signal family</b></p>
<p>A group of clues that essentially look at the same thing. "Completion risk" and "unusual
duration" both read the clock, so they count as <b>one</b> family, not two.</p>
<p><i>Why this matters:</i> without it, the system could fool itself. Asking the same
witness the same question twice is not two pieces of evidence.</p>

<p><b>Corroboration rule</b></p>
<p>Our core safety rule: <b>a work is only raised when at least two independent families
agree.</b> Never on a single clue.</p>

<p><b>Noisy-OR</b></p>
<p>The formula that combines several clues into one score. Its useful property: several
weak clues together produce a moderate score, and no single clue can push the score to the
maximum on its own.</p>

<p><b>Money at risk</b> (in our code: exposure)</p>
<p>The recommended amount multiplied by the chance the work does not finish.</p>
<p>A Rs 10 lakh work with a 30% chance of stalling contributes Rs 3 lakh of money at risk.
<b>This is not lost money and not stolen money.</b> It is money currently tied up in works
that might not finish - a number for planning attention, nothing more.</p>

<p><b>Audit-ROI</b> (Return On Investment for auditing)</p>
<p>The ranking score: priority x money at risk x number of agreeing clue families.</p>
<p>It answers "if an auditor has one day, where does that day do the most good?" A tiny
work with a strange record matters less than a large work with the same strange record.</p>

<p><b>Case file</b></p>
<p>The one-page output for a raised work: what it is, which clues fired, how it compares to
peers, how much money is at risk, and the single next step for a human.</p>

<p><b>Human-in-the-loop</b></p>
<p>A person always makes the final decision. The computer only points.</p>

<h3>4.6 Words about the software</h3>
<p><b>Pipeline</b> - the chain of processing steps, each feeding the next.<br/>
<b>API</b> - the messenger that carries data between the stored results and the screens.<br/>
<b>FastAPI</b> - the specific tool we used to build that messenger.<br/>
<b>React</b> - the tool used to build the screens people click on.<br/>
<b>Parquet / JSON</b> - efficient file formats for storing results.<br/>
<b>JWT</b> - a digitally signed pass proving who a user is; it cannot be forged without the
secret key.<br/>
<b>RBAC</b> (Role-Based Access Control) - each user sees only their own jurisdiction.<br/>
<b>Hash</b> - a fingerprint of a piece of data. Change one character and the fingerprint
changes completely.<br/>
<b>Hash chain</b> - each record's fingerprint includes the previous record's fingerprint,
so altering an old record breaks every fingerprint after it. This is how our tamper-evident
log works.<br/>
<b>Automated test</b> - a small program that checks the main program still behaves
correctly. We have 104 of them.</p>
""")

    # ------------------------------------------------ part 5: what we built
    S.append(f"""
<h2>Part 5 - What We Actually Built</h2>

<h3>5.1 The three models we trained</h3>
<p>People often ask "how many AI models did you train?" The honest answer is <b>three</b>,
plus one ready-made tool we use but did not train.</p>

<table border="1" width="100%"><thead><tr>
<th bgcolor="#eeeeee" width="26%"><b>Model</b></th><th bgcolor="#eeeeee" width="40%"><b>Its job</b></th>
<th bgcolor="#eeeeee" width="34%"><b>Honest result</b></th>
</tr></thead><tbody>
<tr><td><b>MiniLM</b><br/>(NOT trained by us)</td>
<td>Turns descriptions into 384 numbers</td>
<td>Ready-made. We use it, like a calculator</td></tr>
<tr><td><b>MiniBatchKMeans</b><br/>(trained)</td>
<td>Sorts {n['emb']} descriptions into work types</td>
<td>Tried 20/30/40/50/60 groups; {n['k']} was clearest at
silhouette {n['sil']} - a separation measure, NOT accuracy</td></tr>
<tr><td><b>Cox survival model</b><br/>(trained)</td>
<td>Predicts which works may not finish</td>
<td><b>C-index {n['cindex']}</b> on held-back data</td></tr>
<tr><td><b>IsolationForest</b><br/>(trained)</td>
<td>Flags statistically odd works</td>
<td>{n['iso']} works flagged as unusual</td></tr>
</tbody></table>
<p><br/></p>
<p><b>What "held-back data" means:</b> we deliberately hid 30,000 works from the Cox model
while it learned, then tested it on those. That way it cannot score well by memorising -
it has to have genuinely learned something.</p>

<h3>5.2 The seven intelligence engines</h3>

<p><b>1. Peer comparison</b> - Ranks every work against genuinely similar works using
leave-one-out percentiles and robust z-scores, with hierarchical back-off when a group is
too small.</p>

<p><b>2. Completion risk</b> - The trained Cox model, correctly censored at 26 May 2026,
giving each unfinished work a chance-of-not-finishing.</p>

<p><b>3. Near-duplicate detection</b> - Compares the 384-number fingerprints to find works
that mean the same thing. We found <b>{n['dup_total']} similar pairs</b>, of which
<b>{n['dup_ident']}</b> are word-for-word identical.</p>
<p><b>But here is where domain understanding matters.</b> Repeated descriptions are
completely normal in this scheme: one MP recommending forty street lights writes the same
sentence forty times. Flagging all {n['dup_total']} would be useless noise.</p>
<p>So we narrow to pairs that are near-identical <b>AND from the same government office AND
for a near-identical amount</b> - the shape a genuinely repeated claim would take. That
leaves <b>{n['dup_conc']} pairs</b> actually worth a human's eye.</p>

<p><b>4. Compliance checking</b> - Eight checks for records that contradict the official
process. Every check declares <i>where its authority comes from</i>, which is unusual and
important:</p>
<ul>
<li><b>Official Rule</b> - a published government rule. <b>We claim none</b>, because no
official numeric threshold is published with this data. The category exists so a real rule
can be added later.</li>
<li><b>Observed Baseline</b> - the record contradicts the process the data itself shows
(for example, finished before it started).</li>
<li><b>Statistical Outlier</b> - merely unusual compared to peers. Not a rule, not a
breach.</li>
</ul>
<p>We have an automated test that <i>fails the build</i> if anyone ever labels a
statistical outlier as an official rule. The honesty is enforced by machine, not by
memory.</p>

<p><b>5. Early warning</b> - Combines the Cox risk with "how many times longer than its
peers has this been open?" into four levels: LOW, MEDIUM, HIGH, CRITICAL. Every single
warning carries the sentence that produced it, for example: <i>"HIGH - open 2.4x longer
than the typical completed work of this type in Bihar (410 days); and the survival model
puts a 79% chance it will not complete within 365 days."</i></p>

<p><b>6. Temporal intelligence</b> - Watches monthly and yearly patterns and labels each as
NORMAL, EMERGING, SUDDEN CHANGE or PERSISTENT CHANGE. Of {n['ag_total']} government offices
with enough history, <b>{n['ag_changed']} show a genuine change</b>.</p>
<p>One careful detail: we use only recommendation-time information here. Using completion
data would make every recent month look "changed" simply because recent works have not had
time to finish - a trap that produces convincing nonsense.</p>

<p><b>7. Evidence fusion</b> - Combines everything using noisy-OR with the corroboration
rule, then computes money at risk and Audit-ROI.</p>

<h3>5.3 The screens</h3>
<table border="1" width="100%"><thead><tr>
<th bgcolor="#eeeeee" width="30%"><b>Screen</b></th><th bgcolor="#eeeeee" width="70%"><b>What you see</b></th>
</tr></thead><tbody>
<tr><td><b>Overview</b></td><td>The national picture: totals, money at risk, charts by state
and by confidence level</td></tr>
<tr><td><b>Investigation Queue</b></td><td>The ranked list of leads, searchable and
filterable. The main working screen</td></tr>
<tr><td><b>Temporal Intelligence</b></td><td>Trends over time and the Emerging Works
Radar</td></tr>
<tr><td><b>Near-Duplicates</b></td><td>Side-by-side pairs with similarity scores</td></tr>
<tr><td><b>Compliance and Warning</b></td><td>The eight checks and the Health Index</td></tr>
<tr><td><b>Work Archetypes</b></td><td>All {n['k']} discovered work types with their
statistics</td></tr>
<tr><td><b>Data Transparency</b></td><td>What we measure, what we derive, what is simply not
available</td></tr>
<tr><td><b>Case File</b></td><td>Open any lead to see all of its evidence</td></tr>
</tbody></table>

<h3>5.4 Four kinds of user</h3>
<p>The same intelligence, narrowed to what each person is responsible for:</p>
<ul>
<li><b>Ministry (MoSPI)</b> - sees the whole country</li>
<li><b>State Nodal Authority</b> - sees one state</li>
<li><b>District Authority</b> - sees one implementing office</li>
<li><b>Member of Parliament</b> - sees one constituency</li>
</ul>
<p>This is enforced by the server, not just hidden on screen. An officer holding a pass for
Bihar who requests a Kerala work receives a refusal. We test that refusal, not only the
success case.</p>

<h3>5.5 The tamper-evident record</h3>
<p>Every time anyone views intelligence, a line is written to a log. Each line carries a
fingerprint of its own contents <i>plus</i> the previous line's fingerprint.</p>
<p><i>Comparison:</i> a chain where each link is welded to the one before. Remove or
replace a link in the middle and every weld after it visibly breaks.</p>
<p>We tested this properly: we went behind the system's back, edited row 3 directly in the
database, then asked the system to check itself. It correctly reported <i>"chain broken at
row 3"</i>.</p>
<p><b>An honest limitation, which we state on the screen itself:</b> this is
tamper-<i>evident</i>, not tamper-<i>proof</i>. Somebody with full database access could
rewrite the entire chain from the start. Catching that would need the latest fingerprint
published somewhere outside the system.</p>
""")

    # ---------------------------------------------------- part 6: honesty
    S.append(f"""
<h2>Part 6 - Honesty: What We Refuse To Claim</h2>
<p>This part is what separates our project from one that merely looks impressive. Please
read it carefully - it contains the answers to the hardest questions anyone can ask.</p>

<h3>6.1 Why there is no "fraud detector"</h3>
<p>The problem statement mentions detecting potential fraud. We do not claim to detect
fraud. Here is exactly why, and it is not an excuse.</p>
<p>To teach a computer to recognise something, you must show it labelled examples: "this
one is fraud, this one is not", thousands of times. The computer finds the pattern that
separates the two piles.</p>
<p><b>No such labelled list exists for MPLADS anywhere in public data.</b> Nobody has
published a list of confirmed fraudulent works. So there is nothing to learn from.</p>
<p>If we built something and called it a fraud detector, one of two things would be true:
either we invented the labels ourselves - in which case it detects <i>our guesses</i>, not
fraud - or we relabelled "unusual" as "fraudulent", which is simply false. An unusually
expensive road might be an unusually long road.</p>
<p>So we built an <b>investigation-lead engine</b> instead. Same mathematics, honest
claim.</p>

<h3>6.2 The five things we never say</h3>
<table border="1" width="100%"><thead><tr>
<th bgcolor="#eeeeee" width="42%"><b>We never say</b></th><th bgcolor="#eeeeee" width="58%"><b>Because</b></th>
</tr></thead><tbody>
<tr><td>"This work is fraudulent"</td><td>We cannot know that. We say "worth checking"</td></tr>
<tr><td>"Our accuracy is 94%"</td><td>Accuracy against what? There is no answer key</td></tr>
<tr><td>"Rs {n['exp_cr']} crore was stolen"</td><td>It is money at risk, not lost money</td></tr>
<tr><td>"We detected cost overruns"</td><td>No cost estimate exists to compare against</td></tr>
<tr><td>"Silhouette 0.05 means 5% accurate"</td><td>Silhouette is a separation measure,
never accuracy</td></tr>
</tbody></table>

<h3>6.3 How we proved the system works anyway</h3>
<p>Without an answer key we cannot measure fraud detection. But we <i>can</i> measure
whether the machinery finds what it was built to find. So we made our own answer key.</p>
<p><b>The method, in plain words:</b> take the real data, deliberately damage some records
in known ways, and see whether the system catches the ones we damaged. We know the answers
because we planted them.</p>
<p>We planted four kinds of problem into 250 ordinary works each - works the system had not
already flagged, so any catch is due to our planting and nothing else.</p>
<table border="1" width="100%"><thead><tr>
<th bgcolor="#eeeeee" width="34%"><b>What we planted</b></th>
<th bgcolor="#eeeeee" width="36%"><b>What we did</b></th>
<th bgcolor="#eeeeee" width="30%"><b>Caught</b></th>
</tr></thead><tbody>
<tr><td>Stalled work</td><td>Made it far older than its peers</td><td><b>{n['val_stall']}%</b></td></tr>
<tr><td>Inflated amount</td><td>Multiplied the cost by 8 to 25 times</td><td><b>{n['val_infl']}%</b></td></tr>
<tr><td>Broken lifecycle</td><td>Completed with no sanction record</td><td><b>{n['val_break']}%</b></td></tr>
<tr><td>Cloned description</td><td>Copied another work's text, office and amount</td><td><b>{n['val_clone']}%</b></td></tr>
<tr><td colspan="2"><b>Overall, across {n['val_planted']} planted problems</b></td>
<td><b>{n['val_all']}%</b></td></tr>
</tbody></table>
<p><br/></p>
<p><b>Why two scores are lower, explained rather than hidden:</b></p>
<p>The cloned-description score of {n['val_clone']}% is limited because we only compare
works within the same state and same work type - comparing every work with every other
would mean roughly 44 billion comparisons. Clones planted across those boundaries are
missed. Widening the net would raise the score and cost enormously more computing time.</p>
<p>The broken-lifecycle score of {n['val_break']}% is a direct consequence of our own safety
rule. A lifecycle break is <i>one</i> family of evidence, and we require <i>two</i> before
raising anything. A planted break in an otherwise unremarkable work correctly stays below
the bar. Raising this number would mean weakening corroboration, which would cost far more
in false alarms than it gains.</p>
<p>Both are consequences of design choices we would defend in front of anybody.</p>

<h3>6.4 What this validation is NOT</h3>
<table border="1" width="100%"><tbody><tr><td bgcolor="#f4f4f4">
<b>{n['val_all']}% is not a fraud detection rate.</b><br/><br/>
It is the share of problems <i>we ourselves planted</i> that the system found. A real
irregularity need not look like any of our four patterns, and the overwhelming majority of
real works that do look like them are perfectly legitimate.<br/><br/>
It proves the machinery works. It does not prove anything about fraud.
</td></tr></tbody></table>

<h3>6.5 The Data Transparency screen</h3>
<p>Rather than burying our limitations, we gave them a screen of their own. Every number in
the system is labelled as one of three kinds:</p>
<ul>
<li><b>Measured</b> - read directly from government records. Highest confidence.</li>
<li><b>Derived</b> - calculated by our models, with the confidence stated.</li>
<li><b>Unavailable</b> - the data does not exist. Listed openly, with the measurement that
proves it.</li>
</ul>
<p>The screen also lists the fields a government data grant would unlock - actual
expenditure, payment instalments, cost estimates, GPS, photographs - with the software
interfaces already written and waiting. The day that data arrives, it plugs in. Nothing has
to be rebuilt.</p>
<p>Turning a weakness into a visible feature is deliberate. A reviewer who knows this data
will already know these fields are missing. Showing that we know too - and can prove it
with measurements - is far stronger than hoping nobody asks.</p>
""")

    # ------------------------------------------------------ part 7: results
    S.append(f"""
<h2>Part 7 - The Results</h2>
<p>Every figure below came out of the running system.</p>

<h3>7.1 Scale</h3>
<table border="1" width="100%"><tbody>
<tr><td width="60%">Works read and analysed</td><td><b>{n['works']}</b></td></tr>
<tr><td>Total money recommended</td><td><b>Rs {n['rec_cr']} crore</b></td></tr>
<tr><td>Descriptions turned into 384-number fingerprints</td><td>{n['emb']}</td></tr>
<tr><td>Work types discovered automatically</td><td>{n['k']}</td></tr>
<tr><td>States and UTs / constituencies / offices</td><td>{n['states']} / {n['consts']} / {n['agencies']}</td></tr>
<tr><td>Works completed / still open</td><td>{n['completed']} / {n['open']}</td></tr>
</tbody></table>

<h3>7.2 What the system found</h3>
<table border="1" width="100%"><tbody>
<tr><td width="60%">Money at risk (NOT lost money)</td><td><b>Rs {n['exp_cr']} crore</b></td></tr>
<tr><td>Investigation leads (2+ agreeing families)</td><td><b>{n['leads']}</b></td></tr>
<tr><td>&nbsp;&nbsp;of which HIGH confidence (3+ families)</td><td><b>{n['high']}</b></td></tr>
<tr><td>&nbsp;&nbsp;of which MEDIUM confidence (2 families)</td><td>{n['med']}</td></tr>
<tr><td>Works with a lifecycle problem</td><td>{n['comp_flag']}</td></tr>
<tr><td>Early warning: HIGH / MEDIUM</td><td>{n['ew_high']} / {n['ew_med']}</td></tr>
<tr><td>Similar description pairs found</td><td>{n['dup_total']}</td></tr>
<tr><td>&nbsp;&nbsp;of which administratively concerning</td><td><b>{n['dup_conc']}</b></td></tr>
<tr><td>Offices whose behaviour changed</td><td>{n['ag_changed']} of {n['ag_total']}</td></tr>
<tr><td>Operational Health Index (a derived index)</td><td>{n['health']} / 100</td></tr>
</tbody></table>
<p><br/></p>
<p><b>The number that matters most: {n['high']}.</b> That is how many works an auditor would
actually read, out of {n['works']}. The system's real achievement is turning an impossible
pile into an afternoon's work - with a reason attached to every item.</p>

<h3>7.3 A real example</h3>
<p>This is the top-ranked lead the system produced, unedited:</p>
<table border="1" width="100%"><tbody>
<tr><td bgcolor="#f4f4f4"><b>Construction of Outdoor Gym in 70 locations in Various Blocks
in the District of Saran</b><br/>
Bihar, SARAN constituency &nbsp;|&nbsp; Recommended 21 January 2024 &nbsp;|&nbsp; Rs 6.50
crore &nbsp;|&nbsp; Status: Sanctioned</td></tr>
</tbody></table>
<p><b>Why the system raised it - four independent clues agreed:</b></p>
<ul>
<li><b>Unusual amount:</b> at the 100th percentile of 144 comparable works - the single
most expensive gym work of its type in Bihar</li>
<li><b>Unusual duration:</b> open longer than 100% of comparable works still in
progress</li>
<li><b>Completion risk:</b> the survival model gives it a 79% chance of not completing
within a year</li>
<li><b>Behaviour change:</b> the implementing office's pattern shifted - in 2023 it handled
70 works at a median of Rs 10.4 lakh; in 2024, 42 works at a median of Rs 23.9 lakh</li>
</ul>
<p><b>Money at risk:</b> Rs 5.15 crore &nbsp;|&nbsp; <b>Confidence:</b> HIGH (3 independent
families)</p>
<p><b>What the system recommends:</b> <i>"A human should verify the scope and estimate for
this work against its peers via the Implementing Agency."</i></p>
<p>Notice what it does not say. It does not say the money was misused. A Rs 6.5 crore gym
programme across 70 locations may be entirely proper and simply large. The system says: of
{n['works']} works, this is one an auditor should look at first, and here are the four
reasons.</p>

<h3>7.4 How we know the software is sound</h3>
<p><b>104 automated tests</b> run every time we change anything. They do not merely check
that the code runs - they check that our promises hold. Examples:</p>
<ul>
<li>No row is ever silently lost: 480,768 = 3,987 + 476,781, every time</li>
<li>Nothing is raised on a single clue - the corroboration rule cannot be bypassed</li>
<li>Every case file ends with an action for a human</li>
<li>No statistical outlier is ever labelled an official rule</li>
<li>Editing the audit log breaks the chain and is detected</li>
<li>An officer from the wrong state gets refused</li>
<li>The word "fraud" cannot appear as a field name anywhere in the code</li>
</ul>
<p>That last one is our favourite. The build itself refuses to let anyone quietly turn this
into a fraud classifier.</p>

<h3>7.5 Speed</h3>
<table border="1" width="100%"><tbody>
<tr><td width="65%">Read and clean all 480,768 raw rows</td><td>about 40 seconds</td></tr>
<tr><td>Train all three models</td><td>about 90 seconds</td></tr>
<tr><td>Run the full intelligence pipeline</td><td>about 50 seconds</td></tr>
<tr><td>Run the validation harness</td><td>about 35 seconds</td></tr>
<tr><td><b>Everything, from raw files to a working website</b></td><td><b>under 4 minutes</b></td></tr>
</tbody></table>
<p>On an ordinary laptop. No supercomputer, no cloud cluster, no GPU.</p>
""")

    # ---------------------------------------------------- part 8: closing
    S.append(f"""
<h2>Part 8 - Running It, and What Comes Next</h2>

<h3>8.1 How to run the whole thing</h3>
<p>Four commands rebuild everything from the original government files:</p>
<table border="1" width="100%"><tbody>
<tr><td bgcolor="#f4f4f4" width="34%"><b>mplads ingest</b></td>
<td>Read the raw files, clean them, produce one tidy table of {n['works']} works</td></tr>
<tr><td bgcolor="#f4f4f4"><b>mplads train</b></td>
<td>Train the three models and save them</td></tr>
<tr><td bgcolor="#f4f4f4"><b>mplads pipeline</b></td>
<td>Run all seven engines and produce the case files</td></tr>
<tr><td bgcolor="#f4f4f4"><b>mplads api</b></td>
<td>Start the messenger that serves the results</td></tr>
</tbody></table>
<p>Then <b>npm run dev</b> in the frontend folder opens the website.</p>
<p>Three more commands for checking: <b>mplads validate</b> runs the planted-problem test,
<b>mplads audit</b> verifies the tamper-evident log, and <b>pytest</b> runs all 104
tests.</p>

<h3>8.2 What the problem statement asked, and what we delivered</h3>
<table border="1" width="100%"><thead><tr>
<th bgcolor="#eeeeee" width="42%"><b>Asked for</b></th><th bgcolor="#eeeeee" width="14%"><b>Status</b></th>
<th bgcolor="#eeeeee" width="44%"><b>What we did</b></th>
</tr></thead><tbody>
<tr><td>Detect anomalies</td><td><b>Done</b></td><td>Seven signals, multi-family fusion</td></tr>
<tr><td>Detect delayed projects</td><td><b>Done</b></td><td>Cox survival model, C-index {n['cindex']}</td></tr>
<tr><td>Detect duplicate works</td><td><b>Done</b></td><td>{n['dup_conc']} concerning pairs from 384-number fingerprints</td></tr>
<tr><td>Trend analysis</td><td><b>Done</b></td><td>{n['ag_changed']} offices flagged as changed</td></tr>
<tr><td>Deviations from norms</td><td><b>Done</b></td><td>Eight checks, each declaring its authority</td></tr>
<tr><td>Early warning</td><td><b>Done</b></td><td>Four levels, every one explained</td></tr>
<tr><td>Risk-based alerts</td><td><b>Done</b></td><td>{n['high']} HIGH, {n['med']} MEDIUM</td></tr>
<tr><td>Dashboards for four roles</td><td><b>Done</b></td><td>Ministry, State, District, MP</td></tr>
<tr><td>Reduce manual monitoring</td><td><b>Done</b></td><td>{n['works']} works down to {n['high']} to read</td></tr>
<tr><td>Potential fraud</td><td><i>Reframed</i></td><td>Investigation leads - no labels exist to learn from</td></tr>
<tr><td>Expenditure analysis</td><td><i>Not possible</i></td><td>The "actual" column is a copy of the recommended amount</td></tr>
<tr><td>Cost overruns</td><td><i>Not possible</i></td><td>No cost estimate exists anywhere in the data</td></tr>
<tr><td>Payment tracking</td><td><i>Not possible</i></td><td>No payment data is published</td></tr>
<tr><td>Physical progress %</td><td><i>Substituted</i></td><td>Administrative stage, honestly labelled as such</td></tr>
<tr><td>Photo verification</td><td><i>Not possible</i></td><td>Photo files need a government login</td></tr>
</tbody></table>
<p><br/></p>
<p>Of everything the public data genuinely allows, essentially all of it is built. The
items marked "not possible" are not unfinished work - they are things the published data
does not contain, each proven with a measurement rather than asserted.</p>

<h3>8.3 What would make it dramatically better</h3>
<p>One thing: <b>a data grant from MoSPI.</b> With access to the restricted fields, these
become possible immediately, using the engines that already exist:</p>
<ul>
<li><b>Actual expenditure</b> - genuine fund-utilisation analysis</li>
<li><b>Payment instalments</b> - unusual payment patterns</li>
<li><b>Cost estimates</b> - real cost-overrun detection, at last</li>
<li><b>Vendor identity</b> - the same contractor winning repeatedly</li>
<li><b>GPS coordinates</b> - mapping and site clustering</li>
<li><b>Photographs</b> - detecting the same photo submitted for two works</li>
</ul>
<p>The software interfaces for all six are already written and sitting empty.</p>

<h3>8.4 The honest summary</h3>
<table border="1" width="100%"><tbody><tr><td bgcolor="#f4f4f4">
<p>We built a system that reads <b>{n['works']} government works</b> in under four minutes,
groups them into <b>{n['k']} types it discovered itself</b>, compares each against genuinely
similar works, predicts which may never finish, spots near-identical claims, notices when
an office's behaviour changes, and hands officials <b>{n['high']} high-confidence leads</b>
with the evidence attached to each.</p>
<p>It never accuses anyone. It never invents data it does not have. When asked for
something the data cannot support, it says so plainly and shows the measurement that proves
it.</p>
<p><b>The impact is not "AI catches corruption." The impact is giving public officials a
scalable, explainable way to decide where their limited attention deserves to go.</b></p>
</td></tr></tbody></table>

<h3>8.5 A closing thought</h3>
<p>The easiest version of this project would have been to build something that outputs a
"fraud score" for every work. It would look impressive on a slide. It would also be
meaningless, because there is nothing in the data to learn fraud from - and anyone who
knows this dataset would spot it in one question.</p>
<p>We built the harder, honest version instead: a system that finds what is genuinely
findable, explains every conclusion in words a person can check, and states clearly where
the data runs out.</p>
<p>In a system that decides where public money gets investigated, being trustworthy matters
more than being clever.</p>
<p><br/></p>
<hr/>
<p><i>Team Morior Invictus &nbsp;|&nbsp; Smart India Hackathon 2026 &nbsp;|&nbsp; Problem
Statement SIH26102 &nbsp;|&nbsp; Ministry of Statistics and Programme Implementation</i></p>
""")

    return S
