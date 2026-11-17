// History Clock event data — English.
// One entry per year (the clock shows HH:MM as a year, so only years whose last two digits are 00–59 exist).
// t = short dial text (aim ≤45 characters, two lines at most)
// s = status, future years only: "forecast" (certain: astronomy, calendar) or "speculation"
// Years not listed here get a placeholder line from index.html until the real Excel data replaces this file.
window.HC_EVENTS = {
  0:    { t: "The year that never was: 1 BC is followed by AD 1" },
  9:    { t: "Germanic tribes destroy three Roman legions at Teutoburg" },
  313:  { t: "Edict of Milan grants Christians freedom of worship" },
  1215: { t: "King John seals Magna Carta at Runnymede" },
  1609: { t: "Galileo turns his telescope to the night sky" },
  1632: { t: "Academia Gustaviana is founded in Tartu" },
  1917: { t: "Revolution in Russia: the tsar abdicates" },
  1957: { t: "Sputnik 1, the first satellite, beeps its way around Earth" },
  2117: { t: "Venus crosses the face of the Sun, first transit since 2012", s: "forecast" }
};
