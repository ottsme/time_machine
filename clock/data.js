// History Clock: SAMPLE texts only (21 of 1,440), so the public simulator works for anyone.
// The full texts are private (ottsme/history_clock_data). Load them in the simulator: Review > Load texts from file.
// t = dial text; s = future status: scheduled | perhaps | scifi | fact (no label)
window.HC_EVENTS = {
  0: {"t": "Welcome to the History Clock"},
  9: {"t": "Arminius defeats 3 Roman legions in Teutoburg Forest"},
  410: {"t": "Visigoths (Alarich) sack Rome 1st time since 390 BC"},
  800: {"t": "Charlemagne crowned emperor of the Romans"},
  1054: {"t": "Eastern Orthodox and Roman Catholic Church split"},
  1215: {"t": "King John seals Magna Carta, limiting royal power"},
  1347: {"t": "Black Death in Europe, 30% population wiped out"},
  1453: {"t": "Constantinople falls to Turks, end of Byzantine Empire"},
  1517: {"t": "Martin Luther publishes his 95 Theses"},
  1605: {"t": "1st part of M. de Cervantes' Don Quixote published"},
  1632: {"t": "Construction of the Taj Mahal begins"},
  1815: {"t": "Battle of Waterloo, Napoleon exiled to St Helena"},
  1848: {"t": "Marx and Engels publish The Communist Manifesto"},
  1905: {"t": "Albert Einstein: E = mc²"},
  1917: {"t": "October Revolution in Russia, Civil War"},
  1945: {"t": "End of WW2 ○ Nürnberg ○ UN founded"},
  1957: {"t": "Sputnik and Laika in space"},
  2001: {"t": "9/11 attacks in US ○ Apple's iPod"},
  2026: {"t": "Sagrada Familia completed (?); started in 1882"},
  2117: {"t": "First transit of Venus since 2012", "s": "scheduled"},
  2310: {"t": "Voyager I (1977) reaches Oort-Öpik Cloud", "s": "perhaps"}
};
