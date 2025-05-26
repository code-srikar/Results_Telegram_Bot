from typing import Final
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import seleniumbase as sb
from bs4 import BeautifulSoup
from fpdf import FPDF
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN:Final = os.getenv("TOKEN")
BOT_USERNAME = os.getenv("BOT_USERNAME")

SECTION_HTNOS = {
    "C": ["22b81a05c9","22b81a05d0","22b81a05d1","22b81a05d2","22b81a05d3","22b81a05d4","22b81a05d5","22b81a05d6","22b81a05d7","22b81a05d8","22b81a05d9","22b81a05e0","22b81a05e2","22b81a05e3","22b81a05e4","22b81a05e5","22b81a05e6","22b81a05e7","22b81a05e8","22b81a05e9","22b81a05f0","22b81a05f1","22b81a05f2","22b81a05f3","22b81a05f4","22b81a05f5","22b81a05f6","22b81a05f7","22b81a05f8","22b81a05f9","22b81a05g0","22b81a05g1","22b81a05g2","22b81a05g3","22b81a05g4","22b81a05g5","22b81a05g6","22b81a05g7","22b81a05g8","22b81a05g9","22b81a05h0","22b81a05h1","22b81a05h2","22b81a05h3","22b81a05h4","22b81a05h5","22b81a05h6","22b81a05h7","22b81a05h8","22b81a05h9","22b81a05j0","22b81a05j1","22b81a05j2","22b81a05j3","22b81a05j4","22b81a05j5","22b81a05j6","22b81a05j7","22b81a05j8","22b81a05j9","22b81a05k0","22b81a05k1","22b81a05k2"],
    "D": ["22b81a05k3","22b81a05k4","22b81a05k5","22b81a05k6","22b81a05k7","22b81a05k8","22b81a05k9","22b81a05l0","22b81a05l1","22b81a05l2","22b81a05l3","22b81a05l4","22b81a05l5","22b81a05l6","22b81a05l7","22b81a05l8","22b81a05l9","22b81a05m0","22b81a05m1","22b81a05m2","22b81a05m3","22b81a05m4","22b81a05m5","22b81a05m6","22b81a05m7","22b81a05m8","22b81a05m9","22b81a05n0","22b81a05n1","22b81a05n2","22b81a05n3","22b81a05n4","22b81a05n5","22b81a05n6","22b81a05n7","22b81a05n8","22b81a05n9","22b81a05p0","22b81a05p1","22b81a05p2","22b81a05p3","22b81a05p4","22b81a05p5","22b81a05p6","22b81a05p7","22b81a05p8","22b81a05p9","22b81a05q0","22b81a05q1","22b81a05q2","22b81a05q3","22b81a05q4","22b81a05q6","22b81a05q7","22b81a05q8","22b81a05q9","22b81a05r0","22b81a05r1","22b81a05r2","22b81a05r3","22b81a05r4","22b81a05r5","22b81a05r6"],
    # Add more sections and HTNOs
}

# ----- Start Command -----
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Individual Result", callback_data='individual')],
        [InlineKeyboardButton("Section-wise Result", callback_data='section')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose result type:", reply_markup=reply_markup)

# ----- Help Command -----
async def help_command(update:Update,context:ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Available Commands:\n/result <rollno> - Get individual result\n/section <section_name> - Get sorted results by CGPA\n/top10 - Top 10 in the section\n/subscribe - Get result alerts")

# ----- Help Command -----
async def top10_command(update:Update,context:ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) != 4:
        await update.message.reply_text("Usage: /top10 <SECTION> <YEAR> <SEM> <EXAM_TYPE>")
        return

    section, year, sem, exam = args
    htnos = SECTION_HTNOS.get(section.upper(), [])

    if not htnos:
        await update.message.reply_text("Invalid section name.")
        return

    results = extract_top10_results(htnos, year, sem, exam)
    await context.bot.send_document(chat_id=update.effective_chat.id, document=open(results, 'rb'), caption=f"Top 10 Students of Section {section} (PDF)")

# ----- Help Command -----
async def result_command(update:Update,context:ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) != 4:
        await update.message.reply_text("Usage: /result <HTNO> <YEAR> <SEM> <EXAM_TYPE>\nExample: /result 22b81a05d2 III II R")
        return
    
    htno, year, sem, exam = args
    await update.message.reply_text(f"Fetching result for {htno} ({year}-{sem}, {exam})...⏳")

    # Scrape and send result
    result_text = handle_individual_response(htno, year, sem, exam)
    await update.message.reply_text(result_text)

# ----- Help Command -----
async def section_command(update:Update,context:ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) != 4:
        await update.message.reply_text("Usage: /section <SECTION> <YEAR> <SEM> <EXAM_TYPE>\nExample: /section C III I R")
        return

    section, year, sem, exam = args
    htnos = SECTION_HTNOS.get(section.upper(), [])

    if not htnos:
        await update.message.reply_text("Invalid section name.")
        return

    await update.message.reply_text(f"Fetching sorted results for section {section}...⏳")

    result_path = handle_bulk_response(htnos, year, sem, exam)
    await context.bot.send_document(chat_id=update.effective_chat.id, document=open(result_path, 'rb'), caption="Sorted Section Results (PDF)")

# ----- Callback Button Handler -----
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if 'type' not in context.user_data:
        context.user_data['type'] = data
        keyboard = [
            [InlineKeyboardButton("I", callback_data='I')],
            [InlineKeyboardButton("II", callback_data='II')],
            [InlineKeyboardButton("III", callback_data='III')],
            [InlineKeyboardButton("IV", callback_data='IV')],
        ]
        await query.edit_message_text("Select Year:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if 'year' not in context.user_data:
        context.user_data['year'] = data
        sem_keyboard = [
            [InlineKeyboardButton("I", callback_data='I')],
            [InlineKeyboardButton("II", callback_data='II')]
        ]
        await query.edit_message_text("Select Semester:", reply_markup=InlineKeyboardMarkup(sem_keyboard))
        return

    if 'sem' not in context.user_data:
        context.user_data['sem'] = data
        exam_keyboard = [
            [InlineKeyboardButton("R", callback_data='R')],
            [InlineKeyboardButton("S", callback_data='S')],
            [InlineKeyboardButton("M", callback_data='M')],
        ]
        await query.edit_message_text("Select Exam Type:", reply_markup=InlineKeyboardMarkup(exam_keyboard))
        return

    if 'exam' not in context.user_data:
        context.user_data['exam'] = data

        if context.user_data['type'] == 'individual':
            await query.edit_message_text("Please enter your Hall Ticket Number (HTNO):")
            return

        # SECTION-WISE: Show section buttons
        keyboard = [[InlineKeyboardButton(section, callback_data=f"sec_{section}")]
                    for section in SECTION_HTNOS.keys()]
        await query.edit_message_text("Select your section:", reply_markup=InlineKeyboardMarkup(keyboard))
        return
    elif data.startswith("sec_"):
        section = data.split("_")[1]
        context.user_data['section'] = section
        await query.edit_message_text(f"Fetching results for Section {section}... please wait ⏳")

        year = context.user_data['year']
        sem = context.user_data['sem']
        exam = context.user_data['exam']
        htnos = SECTION_HTNOS.get(section, [])

        async def fetch_bulk_and_send():
            results = handle_bulk_response(htnos, year, sem, exam)
            # print(results)
            # CHUNK_SIZE = 4000
            # message = "\n\n".join(results)
            # for i in range(0, len(message), CHUNK_SIZE):
            await context.bot.send_document(chat_id=query.message.chat.id, document=open(results, 'rb'),caption="Here is your PDF of Sorted Results!")

        context.application.create_task(fetch_bulk_and_send())
    context.user_data.clear()

# ----- Result Scraper -----
def handle_individual_response(htno: str,y:str,sm:str,ex:str) -> str:
    # processed_text = text.upper()
    # parts = processed_text.split(" ")
    # if len(parts) == 5:
        # htno = parts[1]
        # y = parts[2]
        # sm = parts[3]
        # ex = parts[4]
    with sb.SB(uc=True, headed=False) as s:
        s.open("https://results.cvr.ac.in/cvrresults1/resulthome.php")
        html = s.get_page_source()
        soup = BeautifulSoup(html, "html.parser")

        for link in soup.find_all("a"):
            if "B.Tech" in link.text and "R22" in link.text and f"{y.upper()} YEAR {sm.upper()} SEM {ex.upper()}" in link.text:
                result_link = "https://results.cvr.ac.in" + link.get("href")
                break
        else:
            return "❌ Result link not found"

        s.open(result_link)
        s.wait_for_element('input[name="srno"]', timeout=5)
        s.type('input[name="srno"]', htno)
        s.wait_for_element('button[type="submit"]', timeout=5)
        s.click('button[type="submit"]')
        s.wait_for_element('table.bttable.blue')

        html = s.get_page_source()
        soup = BeautifulSoup(html, "html.parser")
        tab = soup.find_all("table", class_="bttable")

        name = tab[0].find_all("td")[3].get_text()
        result_data = [f"Name: {name}"]
        for row in tab[2]:
            cells = row.find_all(["th", "td"])
            if cells:
                result_data.append(" | ".join(cell.get_text(strip=True) for cell in cells))

        return result_data
    # else:
    #     return "❗Incorrect format. Use: HTNO 22ABC12343 II I R/S/M (Regular/Supplementary/Minor)"

def handle_bulk_response(htnos:list, year:str, sem:str, exam:str)->str:
    results = []

    with sb.SB(uc=True, headed=False) as s:
        s.open("https://results.cvr.ac.in/cvrresults1/resulthome.php")
        html = s.get_page_source()
        soup = BeautifulSoup(html, "html.parser")

        result_link = None
        for link in soup.find_all("a"):
            if "B.Tech" in link.text and "R22" in link.text and f"{year.upper()} YEAR {sem.upper()} SEM {exam.upper()}" in link.text:
                result_link = "https://results.cvr.ac.in" + link.get("href")
                break

        if not result_link:
            return ["❌ Result link not found"]

        s.open(result_link)

        for htno in htnos:
            try:
                s.wait_for_element('input[name="srno"]', timeout=5)
                s.type('input[name="srno"]', htno)
                s.wait_for_element('button[type="submit"]', timeout=5)
                s.click('button[type="submit"]')
                s.wait_for_element('table.bttable.blue', timeout=5)

                html = s.get_page_source()
                soup = BeautifulSoup(html, "html.parser")
                tab = soup.find_all("table", class_="bttable")

                name = tab[0].find_all("td")[3].get_text()
                result_data = []
                cgpa = 0.0
                for row in tab[2].find_all("tr"):
                    cells = row.find_all(["th", "td"])
                    if cells:
                        line = " | ".join(cell.get_text(strip=True) for cell in cells)
                        result_data.append(line)
                        if "SGPA" in line or "CGPA" in line:
                            try:
                                cgpa = float(cells[-1].get_text(strip=True))
                            except:
                                pass

                results.append((cgpa, name, result_data))
            except Exception as e:
                results.append((0.0, f"{htno} ❌ Error", [str(e)]))

    # Sort by CGPA
    sorted_results = sorted(results, key=lambda x: x[0], reverse=True)

    messages = []
    for cgpa, name, data in sorted_results:
        block = f" {name} - CGPA: {cgpa}\n" + "\n".join(data)
        messages.append(block)

    def generate_pdf(messages, filename="CVR_Results.pdf"):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        for message in messages:
            lines = message.split("\n")
            for line in lines:
                pdf.cell(200, 10, txt=line, ln=True)
            pdf.ln(5)  # Add space between blocks

        # Save the PDF file
        pdf.output(filename)
        return filename
    pdf_path = generate_pdf(messages)
    return pdf_path

def extract_top10_results(htnos:list,year:str,sem:str,exam:str)->str:
    results = []
    # y = year.upper()

    with sb.SB(uc=True, headed=False) as s:
        s.open("https://results.cvr.ac.in/cvrresults1/resulthome.php")
        html = s.get_page_source()
        soup = BeautifulSoup(html, "html.parser")

        result_link = None
        for link in soup.find_all("a"):
            if "B.Tech" in link.text and "R22" in link.text and f"{year.upper()} YEAR {sem.upper()} SEM {exam.upper()}" in link.text:
                result_link = "https://results.cvr.ac.in" + link.get("href")
                break

        if not result_link:
            return ["❌ Result link not found"]

        s.open(result_link)

        for htno in htnos:
            try:
                s.wait_for_element('input[name="srno"]', timeout=5)
                s.type('input[name="srno"]', htno)
                s.wait_for_element('button[type="submit"]', timeout=5)
                s.click('button[type="submit"]')
                s.wait_for_element('table.bttable.blue', timeout=5)

                html = s.get_page_source()
                soup = BeautifulSoup(html, "html.parser")
                tab = soup.find_all("table", class_="bttable")

                name = tab[0].find_all("td")[3].get_text()
                result_data = []
                cgpa = 0.0
                for row in tab[2].find_all("tr"):
                    cells = row.find_all(["th", "td"])
                    if cells:
                        line = " | ".join(cell.get_text(strip=True) for cell in cells)
                        result_data.append(line)
                        if "SGPA" in line or "CGPA" in line:
                            try:
                                cgpa = float(cells[-1].get_text(strip=True))
                            except:
                                pass

                results.append((cgpa, name, result_data))
            except Exception as e:
                results.append((0.0, f"{htno} ❌ Error", [str(e)]))

    # Sort by CGPA
    sorted_results = sorted(results, key=lambda x: x[0], reverse=True)
    
    messages = []
    for cgpa, name, data in sorted_results[:11]:
        block = f" {name} - CGPA: {cgpa}\n" + "\n".join(data)
        messages.append(block)

    def generate_pdf(messages, filename="CVR_Results.pdf"):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        for message in messages:
            lines = message.split("\n")
            for line in lines:
                pdf.cell(200, 10, txt=line, ln=True)
            pdf.ln(5)  # Add space between blocks

        # Save the PDF file
        pdf.output(filename)
        return filename
    pdf_path = generate_pdf(messages)
    return pdf_path


# ----- Handle HTNO Input After Button Flow -----
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    text: str = update.message.text

    if 'type' in context.user_data and context.user_data['type'] == 'individual' and 'exam' in context.user_data:
        htno = text
        year = context.user_data['year']
        sem = context.user_data['sem']
        exam = context.user_data['exam']
        formatted = f"HTNO {htno} {year} {sem} {exam}"

        await update.message.reply_text("Fetching your result... please wait ⏳")

        async def fetch_and_reply():
            response = handle_individual_response(formatted)
            await context.bot.send_message(chat_id=chat_id, text=response)

        context.application.create_task(fetch_and_reply())
    else:
        await update.message.reply_text("Please use /start and follow the button prompts to get results.")

# ----- Error Handler -----
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")

# ----- Main -----
if __name__ == "__main__":
    print("Starting bot...")
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(CommandHandler("result", result_command))
    app.add_handler(CommandHandler("section", section_command))
    app.add_handler(CommandHandler("top10", top10_command))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_error_handler(error)

    print("Polling...")
    app.run_polling(poll_interval=3)
