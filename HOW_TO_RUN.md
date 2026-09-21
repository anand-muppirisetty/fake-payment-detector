# HOW TO RUN THIS PROJECT — Read this every time you forget

## Every time you want to open the project:

1. **Open Docker Desktop** (the app) — wait until the whale icon settles/stops loading
2. **Open a terminal inside this folder:**
   - Windows: open this folder in File Explorer → click the address bar → type `cmd` → Enter
   - Mac: open this folder in Finder → right-click empty space → "New Terminal at Folder"
3. **Type this one line and press Enter:**
   ```
   docker compose up
   ```
4. **Open your browser and go to:**
   ```
   http://localhost:5173
   ```

## To stop it:
Go to the terminal window that's running, press `Ctrl + C`

## If you changed any code and want those changes to show up:
Use this instead of step 3 (rebuilds with your changes):
```
docker compose up --build
```

## If something breaks / login or buttons don't work:
1. In Docker Desktop → Containers → click on `backend` → check the **Logs** tab for red error text
2. Copy that error text and ask Claude to help debug it
3. As a first thing to try: stop everything (`Ctrl + C`), then run `docker compose up --build` again

## Login note:
Every time you rebuild containers from scratch (`--build` after deleting old containers), your
old accounts/data are gone — you'll need to register a new account again at
`http://localhost:5173/register`.
