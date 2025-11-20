# AI-Project Quick Reference Card
**Print this and keep it handy!**

---

## Starting the App

### Step 1: Open Docker Desktop
Look for the whale icon - must say "running"

### Step 2: Open Terminal in Project Folder
**Mac:** Right-click folder → "New Terminal at Folder"
**Windows:** In File Explorer → Click address bar → Type `cmd` → Enter

### Step 3: Start Container
**Mac/Linux:**
```bash
./scripts/run_local.sh
```

**Windows:**
```bash
docker-compose up
```

### Step 4: Open Browser
Go to: **http://localhost:5000**

---

## Stopping the App

**In Terminal:** Press **Ctrl+C**

**OR in Docker Desktop:**
- Containers → ai-project-dev → Click Stop

---

## Daily Workflow

1. Open Docker Desktop (must be running)
2. Open Terminal in project folder
3. Run `./scripts/run_local.sh` (Mac) or `docker-compose up` (Windows)
4. Open browser to http://localhost:5000
5. Edit code in your editor → Save
6. Refresh browser (F5) to see changes
7. Stop container when done (Ctrl+C)

---

## Common Problems

| Problem | Solution |
|---------|----------|
| "Cannot connect to Docker" | Open Docker Desktop, wait for "running" |
| "Port 5000 already in use" | Stop other containers in Docker Desktop |
| Changes not showing | Hard refresh: **Ctrl+Shift+R** (Win) or **Cmd+Shift+R** (Mac) |
| Can't see `.env.development` | **Windows:** File Explorer → View → Hidden items<br>**Mac:** Finder → Press **Cmd+Shift+.** |
| API key errors | Check `.env.development` has keys, no spaces around `=` |

---

## Important Files

| File | What It Does |
|------|--------------|
| `.env.development` | Your API keys (keep private!) |
| `ui/app.py` | Main application code |
| `ui/templates/` | HTML pages |
| `ui/static/` | CSS, JavaScript |
| `models/ocr_processor.py` | Image processing |

---

## Useful URLs

| What | URL |
|------|-----|
| **Your App** | http://localhost:5000 |
| **Health Check** | http://localhost:5000/health |
| **GitHub Repo** | https://github.com/twburns88/ISYS57103-Fall25-GroupProject-Thomas-Lalitsingh-Peggy |
| **Docker Desktop** | https://www.docker.com/products/docker-desktop |

---

## Git Commands (via GitHub Desktop)

### Get Latest Changes
1. Open GitHub Desktop
2. Click **"Fetch origin"** (top right)
3. Click **"Pull origin"** if changes available
4. Restart Docker container

### Share Your Changes
1. Open GitHub Desktop
2. See your changes listed on left
3. Write description in "Summary" box
4. Click **"Commit to main"**
5. Click **"Push origin"**

---

## Quick Health Check

**Is everything working?**
- [ ] Docker Desktop shows green icon (running)
- [ ] Terminal shows "Running on http://0.0.0.0:5000"
- [ ] Browser loads http://localhost:5000
- [ ] Can upload an image
- [ ] OCR processes the image
- [ ] Can search and see results

**All checked?** You're good!

---

## Need Help?

1. Check `docs/TEAM_SETUP_GUIDE.md` (detailed instructions)
2. Check `docs/DOCKER_SETUP.md` (technical details)
3. Ask Thomas!

---

**Remember:**
- Keep Docker Desktop running while you work
- Save often (Ctrl+S / Cmd+S)
- Refresh browser after changes (F5)
- Never commit `.env.development` (has API keys!)

**Print this page and keep it at your desk!**
