/**
 * Plain-language "what this chart means" blurbs shown in each chart's "?" tooltip.
 * Kept here so the panels stay small and the wording lives in one place.
 */
export const CHART_INFO = {
  trend:
    "Each point is one completed session, oldest to newest. Mastery and " +
    "confidence (left axis, 0–100%) show how much you've learned and how sure " +
    "you feel. Misconfidence (right axis) compares the two: it's positive when " +
    "your confidence matches how well you actually do (solid understanding), and " +
    "negative when you're confident but wrong — a misconception risk. Coral dots " +
    "mark sessions where a specific misconception was detected.",
  misconceptionDonut:
    "Each slice is a type of misconception the tutor spotted across your " +
    "completed sessions, sized by how often it came up. A bigger slice means " +
    "that mistake pattern showed up more — a good place to focus next.",
  subjectBars:
    "For each subject, the bars show your average mastery and confidence across " +
    "all of its sessions. A confidence bar much taller than mastery hints at " +
    "over-confidence; a shorter one means you likely know more than you think.",
  topicRanking:
    "Every topic you've practised, ranked strongest to weakest by mastery. The " +
    "bar colour flags where to focus — green is solid, amber is getting there, " +
    "and coral needs work.",
  masteryConfidence:
    "For each topic, your mastery sits next to your confidence. A taller " +
    "confidence bar than mastery flags over-confidence — feeling sure on a topic " +
    "you haven't fully nailed yet.",
  effort:
    "Each bubble is a topic: how many times you've practised it (left to right) " +
    "versus your current mastery (bottom to top), with bubble size showing your " +
    "streak. Big bubbles low down mean lots of effort with little to show yet — " +
    "topics worth a fresh approach.",
  understanding:
    "How your topics split across “got it”, “getting there” and “stuck”, based " +
    "on the tutor's read of your answers. More green means more topics you've " +
    "genuinely understood.",
  reviewDue:
    "Topics with a spaced-repetition review coming up, soonest first, alongside " +
    "your current mastery. Reviewing just before you'd forget is the fastest way " +
    "to make learning stick.",
} as const;
