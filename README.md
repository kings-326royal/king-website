# Dr. G. R. Gnana King – Profile Website

A single-page academic profile with downloadable biodata. It runs on GitHub Pages with no server.

| File | What it is |
| --- | --- |
| `index.html` | The website: profile, statistics, all records, download box and the editor |
| `data.js` | All your records (publications, patents, grants and so on). The site reads this file. |
| `metrics.js` | Citation figures, refreshed automatically (do not edit by hand) |
| `scripts/update_metrics.py` | Fetches the citation figures |
| `.github/workflows/update-metrics.yml` | Runs the fetcher on GitHub every week |
| `.nojekyll` | Tells GitHub Pages to serve the files as they are |

## What visitors can do

- See the headline statistics and three charts: publications by type, journal papers by indexing, and publications per year.
- Read every section (experience, publications, patents, grants, service, awards, training).
- Pick a **Document** and a **File type**. Only you (and visitors you approve) can download; see *Download requests* below.

| Document | File types |
| --- | --- |
| One-page infographic (colour) | PDF, PNG image, Word |
| One-page summary (professional) | PDF, Word |
| Standard resume (2–3 pages) | PDF, Word |
| Full biodata (every record, nothing omitted) | PDF, Word |

- Press **Show preview** to see the document before downloading (also only for you and approved visitors).

The files are built in the browser from `data.js`, so they always match the website.

## Put it on GitHub Pages (one time)

1. Sign in at github.com and create a new **public** repository, for example `gnanaking-profile`.
2. Open the repository, click **Add file → Upload files**, and drag in the **whole contents** of this folder: `index.html`, `data.js`, `metrics.js`, `README.md`, `.nojekyll`, and the `scripts` and `.github` folders. Click **Commit changes**. Folders starting with a dot are hidden on a Mac; press Cmd+Shift+. in Finder to show them before dragging.
3. Go to **Settings → Pages**. Under **Build and deployment**, choose **Deploy from a branch**, branch `main`, folder `/ (root)`, and click **Save**.
4. After about a minute the site is live at `https://<your-username>.github.io/gnanaking-profile/`.

If you name the repository `<your-username>.github.io`, the site lives at `https://<your-username>.github.io/`.

## Download requests

Visitors see the document list but get **Request download** instead of **Download**. They enter their name, email and an optional purpose, and the request is emailed to you through [FormSubmit](https://formsubmit.co) (free, no account). It goes to **Email for download requests** in **Edit profile details**, or to your first email if that is blank.

**One-time setup**

1. On your own computer, open the live site, click **Update records**, open **Download access** and click **Set up this device**. Then click **Publish to GitHub**. From now on this browser downloads everything without a request.
2. Click **Save key file** and keep the file somewhere private. To use another computer or phone, open **Download access** there and choose **Import key file**.
3. Send yourself a test request from a private window. The first time, FormSubmit emails you an **Activate** link; click it, or no requests will reach you.

**Approving a request**

Open the link in the request email on your set-up device. The download box shows who asked and for what. Click **Approve and email the link**: your email app opens a reply containing a download link for that document, valid for 30 days. **Approve and copy the link** copies it instead. To decline, simply do not approve.

If you click **Create a new key**, links approved earlier stop working.

This is a static site, so the records themselves are visible on the page to everyone. The request step controls the ready-made downloads, not the data, and a technically skilled person could get around it.

## Update your records later

Open your live site and click **Update records** at the bottom of the page. You can also add `#edit` to the address. The editor appears in the left column.

- **Edit mode** adds **+ Add** to every section and **Edit / ↑ / ↓ / Delete** to every record.
- Tick **Show in resume and summary** on the records that should appear in the standard resume and one-page summary. The full biodata always includes everything.
- **Edit profile details** (in the About section) holds the photo, citations, h-index, areas of expertise, key contributions and the mission statement shown on the infographic. Choose a photo there; it is cropped to a square and stored inside `data.js`.
- In a citation, put text between `*single stars*` for italics (journal names) or `**double stars**` for bold.
- Your edits are kept in this browser until you publish them. Visitors see nothing until you publish.

Then publish in one of two ways.

### Option A: one click (recommended)

Create a GitHub access token once:

1. On GitHub, open **Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token**.
2. Under **Repository access**, choose **Only select repositories** and pick your profile repository.
3. Under **Permissions → Repository permissions**, set **Contents** to **Read and write**.
4. Generate the token and copy it. It starts with `github_pat_`.

On your site, open **GitHub settings** in the editor. Enter the repository (for example `yourname/gnanaking-profile`), branch `main`, file `data.js` and the token. Click **Save settings on this device**. From then on, **Publish to GitHub** writes your changes to the repository, and the live site updates within about a minute.

The token is stored only in that browser on that computer. Use it only on your own device, and delete the token on GitHub if the device is shared or lost.

### Option B: upload the file

Click **Download data.js** in the editor. On GitHub, open the repository, click **Add file → Upload files**, drop in the new `data.js` (it replaces the old one) and commit.

### Option C: edit by hand

`data.js` is plain JSON after `window.CV_DATA =`. You can open it on GitHub, click the pencil icon, edit, and commit.

## How the statistics stay exact

Every figure at the top of the page is counted from your records each time the page loads:

- Add a journal paper and "Journal publications" and "Total publications" go up by one.
- Add a grant and "Total funding received" adds that exact amount. You can type the amount as `1000000`, `10,00,000` or `10 lakh`.
- Years of experience is the current year minus the career start year in your profile.

The same figures are used in all four downloads, so the files always agree with the website.

## Automatic citation figures (Google Scholar, Scopus, Web of Science)

`scripts/update_metrics.py` reads your IDs from `data.js`, fetches the latest figures and writes `metrics.js`. The website shows citations, h-index, i10-index, documents, citations per year and your most cited papers from that file.

GitHub runs it for you through `.github/workflows/update-metrics.yml`:

- every Monday at 08:00 IST,
- whenever `data.js` changes (for example after you publish an edit), and
- whenever you press **Actions → Update citation metrics → Run workflow** on GitHub.

**One-time setup:** in your repository go to **Settings → Actions → General → Workflow permissions**, choose **Read and write permissions** and save. Without this the job cannot save `metrics.js`.

| Source | What you need |
| --- | --- |
| Google Scholar | Nothing. It works from your Scholar ID. |
| Scopus | A free API key from https://dev.elsevier.com ("I want an API key"). Add it under **Settings → Secrets and variables → Actions → New repository secret**, named `SCOPUS_API_KEY`. |
| Web of Science | A free "Web of Science Starter API" key from https://developer.clarivate.com. Add it as a repository secret named `WOS_API_KEY`. |

Until a key is added, that source shows "Not connected yet" on the website, and the other sources still work. If one fetch fails (Google Scholar sometimes blocks automated visits), the site keeps the previous figures and the next weekly run tries again.

The page uses the first available source for the headline citation and h-index tiles, in this order: Google Scholar, Scopus, Web of Science. If none is available, it uses the manual citation and h-index values in **Edit profile details**.

## Notes

- PDFs show the rupee sign as "Rs." because the built-in PDF font has no ₹ character. Word files keep ₹.
- The infographic is a picture of the page, so its text cannot be selected in the PDF or Word file. Use the one-page summary when text must be copyable.
- The page loads fonts and four small libraries (JSZip, jsPDF, jsPDF-AutoTable, html2canvas) from public CDNs, so downloads need an internet connection.
- To look at the site on your computer before uploading, double-click `index.html`. Everything works locally except **Publish to GitHub**, which also works locally once the token is set.
