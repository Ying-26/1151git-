from fastapi import FastAPI, Depends, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from .db import getDB, lifespan

templates = Jinja2Templates(directory="templates")
app = FastAPI(lifespan=lifespan)

# 掛載靜態檔案資料夾 (供靜態網頁使用)
app.mount("/w", StaticFiles(directory="www"), name="w")

# 1. 取得學生 JSON 資料 (備用/API)
@app.get("/students/list")
async def read_users(db=Depends(getDB)):
    cur = await db.execute("SELECT * FROM students")
    return await cur.fetchall()

# 2. 顯示學生列表頁面
@app.get("/students/list/template")
async def stuList(request: Request, db=Depends(getDB)):
    cur = await db.execute("SELECT * FROM students ORDER BY stuid;")
    data = await cur.fetchall()
    return templates.TemplateResponse(name="studentList.html", request=request, context={"students": data})

# 3. 點擊 Edit 開啟編輯頁面
@app.get("/students/edit/template/{stuid}")
@app.get("/student/edit/{stuid}")
async def stuEdit(stuid: str, request: Request, db=Depends(getDB)):
    cur = await db.execute("SELECT * FROM students WHERE stuid=%s;", (stuid,))
    data = await cur.fetchone()
    return templates.TemplateResponse(name="studentEdit.html", request=request, context={"data": data})

# 4. 提交編輯表單，更新學生資料
@app.post("/student/update")
async def stuUpdate(stuid: str = Form(...), name: str = Form(...), height: str = Form(None), db=Depends(getDB)):
    await db.execute("UPDATE students SET name=%s, height=%s WHERE stuid=%s;", (name, height, stuid))
    return RedirectResponse(url="/students/list/template", status_code=303)

# 5. 新增學生功能
@app.post("/students/add/template")
async def add_student_template(
    stuid: str = Form(...),
    name: str = Form(...),
    height: str = Form(None),
    db=Depends(getDB)
):
    await db.execute(
        "INSERT INTO students (stuid, name, height) VALUES (%s, %s, %s);",
        (stuid, name, height)
    )
    return RedirectResponse(url="/students/list/template", status_code=303)

# 6. 刪除學生功能
@app.post("/students/delete/template/{stuid}")
async def delete_student_template(
    stuid: str,
    db=Depends(getDB)
):
    await db.execute("DELETE FROM students WHERE stuid = %s;", (stuid,))
    return RedirectResponse(url="/students/list/template", status_code=303)