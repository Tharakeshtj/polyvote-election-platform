# Task cards

The moderator reads each card aloud and hands it over. Say nothing else about how to do it. Start the timer when the participant starts, stop when they say they are done or you see the result. After each task ask: **"Overall, how easy or difficult was that? 1 = very difficult, 7 = very easy."**

Before each participant: reset the demo (admin Settings, Factory reset). Voter participants use a different voter each time (`25BCE0019` to `25BCE0030`, password `vote123`); a reset makes all of them available again.

## Voter group

| # | Card text | Success means | Time limit |
|---|---|---|---|
| V1 | "You are a student voter. Open the site and find where to vote." | Reaches the voter sign-in page | 2 min |
| V2 | "Sign in with registration number `25BCE00xx` and password `vote123`." | Passes sign-in and reaches the code step | 2 min |
| V3 | "Get past the one-time code step." | Enters the code from the demo box | 2 min |
| V4 | "Choose your top three candidates in your order of preference, then cast your vote." | Ranks three, reviews, casts | 4 min |
| V5 | "Save a proof that your vote was recorded." | Copies or notes the receipt token | 2 min |
| V6 | "Check that your vote was recorded and counted." | Pastes the token on Check receipt and reads the result | 3 min |
| V7 | "Try to vote a second time." | Sees and reads the refusal; moderator asks "what does it say?" | 2 min |

## Administrator group

| # | Card text | Success means | Time limit |
|---|---|---|---|
| A1 | "You run a club election. Sign in as administrator (`admin` / `admin123` on the demo)." | Reaches the admin area | 2 min |
| A2 | "Create a new election named 'Club president' with three candidates." | Election and three candidates exist | 5 min |
| A3 | "Register two voters with their registration numbers." | Two voters listed | 4 min |
| A4 | "Open voting, then close it." | State shows closed | 3 min |
| A5 | "Find the result. Who won?" | Reads the winner and the rounds | 3 min |
| A6 | "Check that nobody tampered with the election." | Runs the integrity sweep and reads "no tampering" | 3 min |
| A7 | (Moderator opens DB Studio and deletes one ballot of the sample election beforehand.) "Run the same check on the sample election. What does it tell you, and what would you do next?" | Says a ballot was deleted and can name an action (investigate, stop, restore) | 4 min |

## Probe questions at the end (both groups)

1. What was the most confusing moment?
2. Did the receipt token mean anything to you? What do you think it proves?
3. If your club used this, would you trust the result more than a spreadsheet? Why or why not?
