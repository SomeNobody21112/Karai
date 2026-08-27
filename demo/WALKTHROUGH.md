# Field verification - demonstration walkthrough

Everything below runs on real portfolio rows. The photographs are generated renderings of the display board MPLADS already requires at every work site; the verification records are marked as demonstration data and are excluded from the label count on the Data Transparency screen.

## Before you start

1. Sign in at `/login` as **auditor** (password `mplads2026`).
2. Open the case file for `MP3018356-W86316`.
3. Scroll to **Field verification**.

## The four things to show

### 1. It reads the board

Upload `demo/photos/01-board-matches.png`. The reader pulls the work reference and the sanctioned amount off the board and confirms it matches `MP3018356-W86316` - nobody types a reference number standing in a field.

### 2. It notices when the board is for a different work

Upload `demo/photos/02-board-different-work.png` on the same case file. The reference read from the board is shown against the one you are on, and they do not agree. The officer sees the disagreement before saving, not after.

### 3. It catches a recycled photograph - the one a human cannot do at scale

Upload `demo/photos/03-photo-first-submission.png` on `MP3017167-W136962` and record any outcome. Then open `MP3017167-W136963` and upload `demo/photos/04-photo-resubmitted.jpg`.

It is a different file - different name, different format, different size, different SHA-256. The perceptual hash matches anyway, and the screen says which work the picture was already submitted for, by whom, and when.

Say this out loud: **it is a question, not a finding.** Two phases of one road legitimately look identical from the roadside. The system asks; a human answers.

### 4. It admits when it cannot read

Upload `demo/photos/05-board-weathered.png`. Faded and out of focus, the way boards actually look. Confidence drops and the fields come back partial or empty - shown as such, for the officer to correct, never quietly guessed.

## The closing line

Everything else in this product ends at *a human should check X*. This is the only screen that records what the human found - and those records are the only ground truth this system can ever obtain. The Data Transparency screen counts how far off that is instead of implying it has already happened.

## The files

| File | What it shows |
| --- | --- |
| `01-board-matches.png` | A clean board for MP3018356-W86316. It reads, and it matches the case file you are standing in. |
| `02-board-different-work.png` | A board for MP3019436-W119849. Upload it on MP3018356-W86316's case file and the reader says so instead of accepting it. |
| `03-photo-first-submission.png` | Submitted first, for MP3017167-W136962. |
| `04-photo-resubmitted.jpg` | The same photograph resized, re-compressed and brightened, then submitted for MP3017167-W136963. A different file; the same picture. |
| `05-board-weathered.png` | Faded and out of focus, the way boards actually look. Shows what the reader does when it is unsure rather than pretending it is not. |
