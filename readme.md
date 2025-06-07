
###  Setting Up Scheduled Task for `expire_reservations`

This project includes a periodic Django management command that **automatically marks past-due reservations as expired**, unless they were already used or canceled.

The command is located at:

```
reservations/management/commands/expire_reservations.py
```

It should be run **every 2 minutes** for best results.

---

##  How to Set It Up

---

###  For Linux Users

1. **Open your crontab**:

   ```bash
   crontab -e
   ```

2. **Add the following line** (adjust paths as needed):

   ```
   */2 * * * * /path/to/your/venv/bin/python /full/path/to/manage.py expire_reservations >> /tmp/expire_reservations.log 2>&1
   ```

   * Replace `/path/to/your/venv/bin/python` with the path to your Python binary.
   * Replace `/full/path/to/manage.py` with the absolute path to your Django project's `manage.py`.

3. Save and exit. The task will now run every 2 minutes.

---

###  For macOS Users

macOS uses the same crontab system as Linux:

1. Run:

   ```bash
   crontab -e
   ```

2. Add:

   ```
   */2 * * * * /path/to/python /full/path/to/manage.py expire_reservations >> /tmp/expire_reservations.log 2>&1
   ```

Use `which python3` if you're unsure of the path.

---

###  For Windows Users

Use **Task Scheduler** to create a scheduled task.

#### Steps:

1. Open **Task Scheduler** → Click **Create Basic Task**.

2. Set a name like `ExpireReservationsJob`.

3. Set the trigger to **Daily**, and **repeat every 2 minutes**.

4. For **Action**, choose **Start a program**.

5. **Program/script**:

   ```
   C:\Path\To\python.exe
   ```

6. **Add arguments**:

   ```
   manage.py expire_reservations
   ```

7. **Start in (optional)**:

   ```
   C:\Full\Path\To\Your\Django\Project\
   ```

8. Click **Finish**.

 Now the task will run every 2 minutes and mark expired reservations.

---

###  Testing It Manually

To test the command manually:

```bash
python manage.py expire_reservations
```

You should see:

```
Expiring X codes…
Done.
```

---

If you have any issues, make sure:

* Your environment variables are set (e.g., `DJANGO_SETTINGS_MODULE`)
* Your virtual environment is activated or the correct Python path is used
* Your database and model migrations are up-to-date

---

Let me know if you'd like the same README in Markdown format (`README.md`) or with localization support (e.g., Persian).
