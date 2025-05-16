# 🧾 FastAPI + SQLite Mini Project – API for Products, Buyers, and Orders

I built a basic backend project using **FastAPI** and **SQLite** that handles data for products, buyers, and purchases. The app supports full **CRUD operations**, so you can create, read, update, and delete records easily.

Here’s what it manages:
- Products (like items for sale)
- Buyers (customers)
- Purchases (orders placed by buyers)

No need to manually create any tables — they get auto-generated when the server starts, which makes setup super simple.

---

## ⚙️ How I Set It Up

### 1. Cloned the GitHub repo

```bash
git clone https://github.com/bhargavpeddi/final_project_websys.git
cd final_project_websys
```


2. Created a virtual environment and activated it
bashpython -m venv myenv
myenv\Scripts\activate  # for Windows


3. Installed the required libraries
pip install fastapi uvicorn

4. Ran the FastAPI server
uvicorn main:app --reload
