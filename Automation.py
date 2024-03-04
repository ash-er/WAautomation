import io
import json
import os
import pandas as pd
from datetime import datetime
from flask import Flask, render_template, request, Response, jsonify
import matplotlib
from matplotlib import pyplot as plt
matplotlib.use('Agg')
from playwright.sync_api import sync_playwright

app = Flask(__name__)

user_data_path_ = "\\Default_WA_personal_my"  # For Chromium:: "C:\\Users\\tyagi\\AppData\\Local\\ms-playwright
# \\chromium-1097 # Default_WA_Business

# \\chrome-win\\persistent_user_data"

logs = {}


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/wa_automation', methods=['POST'])
def wa_automation():
    # def custom_json_encoder(obj):
    #     if isinstance(obj, bytes):
    #         return obj.decode('utf-8')
    #     raise TypeError("Type not serializable")

    media = request.files.get('media_content')
    Text = request.form.get('message')
    recptnts = request.form.get('recipients')
    bulk_file = request.files.get('bulkFile')
    print(media)
    print(Text)
    print(recptnts)

    recptnts = recptnts.split("\n")
    recptnts = [name.strip() for name in recptnts if name.strip()]

    if media:
        media.save(media.filename)
        media = media.filename
    else:
        media = None

    with sync_playwright() as p:
        context = p.firefox.launch_persistent_context(user_data_path_, headless=False)  # , headless=False
        page = context.new_page()
        page.goto('https://web.whatsapp.com')
        page.wait_for_load_state("load")
        page.wait_for_timeout(5000)

        if bulk_file:
            bulk_file.save(bulk_file.filename)
            bulk_file = bulk_file.filename
            all_sheets_data = pd.read_excel(bulk_file, sheet_name=None)

            flat_list = []
            for sheet_name, sheet_data in all_sheets_data.items():
                flat_list.extend(map(str, sheet_data.values.flatten().tolist()))

            # print(flat_list)

            for number in flat_list:
                # number = "7683024210"
                selector = f'div._3ndVb.fbgy3m38.ft2m32mm.oq31bsqd.nu34rnf1[title="New chat"]'
                page.wait_for_selector(selector)
                page.click(selector)
                page.wait_for_timeout(2000)
                selector2 = "p.selectable-text.copyable-text.iq0m558w.g0rxnol2"
                # page.wait_for_selector(selector2)
                page.fill(selector2, number)
                page.wait_for_timeout(5000)
                page.keyboard.press('Enter')
                page.wait_for_timeout(2000)
                if media is not None:
                    selector3 = 'div._3ndVb[aria-label="Attach"]'
                    page.click(selector3)
                    page.wait_for_timeout(2000)
                    # selector4 =
                    # page.wait_for_selector(selector4)
                    file_input = page.locator('input[accept="image/*,video/mp4,video/3gpp,video/quicktime"]')
                    file_input.set_input_files(media)
                    page.wait_for_timeout(3000)
                if Text is not None:
                    selector5 = 'div[title="Type a message"]'
                    page.wait_for_selector(selector5)
                    page.fill(selector5, Text)
                page.wait_for_timeout(4000)
                page.keyboard.press('Enter')
                tmstmp = datetime.timestamp(datetime.now())
                tmstmp = datetime.utcfromtimestamp(tmstmp).strftime('%Y-%m-%d %H:%M:%S')
                logs[number] = tmstmp
                page.wait_for_timeout(3000)

            os.remove(bulk_file)

        if recptnts:
            for name in recptnts:
                page.wait_for_timeout(3000)
                selector = "div.to2l77zo.gfz4du6o.ag5g9lrv.bze30y65.kao4egtt.qh0vvdkp"
                # page.wait_for_selector(selector)
                page.fill(selector, name)
                page.wait_for_timeout(2000)
                selector2 = f'span.ggj6brxn.gfz4du6o.r7fjleex.g0rxnol2.lhj4utae.le5p0ye3.l7jjieqr._11JPr[title^="{name}"]'
                # page.wait_for_selector(selector2)
                page.click(selector2)
                page.wait_for_timeout(2000)
                if media is not None:
                    # selector4 =
                    # page.wait_for_selector(selector4)
                    selector3 = 'div._3ndVb[aria-label="Attach"]'
                    page.click(selector3)
                    page.wait_for_timeout(2000)
                    file_input = page.locator('input[accept="image/*,video/mp4,video/3gpp,video/quicktime"]')
                    file_input.set_input_files(media)
                    page.wait_for_timeout(3000)
                if Text is not None:
                    page.wait_for_timeout(3000)
                    selector5 = 'div[title="Type a message"]'
                    page.wait_for_selector(selector5)
                    page.fill(selector5, Text)
                page.wait_for_timeout(4000)
                page.keyboard.press('Enter')
                tmstmp = datetime.timestamp(datetime.now())
                tmstmp = datetime.utcfromtimestamp(tmstmp).strftime('%Y-%m-%d %H:%M:%S')
                logs[name] = tmstmp
                page.wait_for_timeout(3000)

        page.wait_for_timeout(10000)
        # page.wait_for_timeout(6000000)

        if media:
            os.remove(media)

        context.close()

    print('Successfully navigated using saved authentication state.....JOB COMPLETE\n', logs)
    # return jsonify('Successfully navigated using saved authentication state.....JOB COMPLETE\n', logs)
    return render_template("logs_table.html", logs=logs)
    # return jsonify(media, Text, recptnts)
    # return json.dumps((media, Text, recptnts), ensure_ascii=False, default=custom_json_encoder)


def generate_pdf(df):
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.axis('tight')
    ax.axis('off')
    ax.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center')

    # Save the figure as a PDF
    pdf_output = io.BytesIO()
    plt.savefig(pdf_output, format='pdf')
    pdf_output.seek(0)

    plt.close(fig)

    return pdf_output.read()


@app.route('/download_pdf')
def download_pdf():
    # Generate DataFrame from sample data
    df = pd.DataFrame(list(logs.items()), columns=['Sent to', 'Timestamp'])

    # Set up response to send PDF as a file download
    response = Response(
        generate_pdf(df),
        mimetype='text/pdf',
        headers={'Content-Disposition': 'attachment; filename=data.pdf'}
    )
    return response


if __name__ == "__main__":
    # file_path = "WhatsappMssg.txt"
    # recp_path = "WhatsappRecpt.txt"
    # content_pic_vid = "movie.MP4"
    #
    # with open(file_path, 'r', encoding='utf-8') as file:
    #     file_contents = file.read()
    #
    # with open(recp_path, 'r', encoding='utf-8') as file:
    #     recp = file.read()
    #     recp_list = recp.split("\n")
    #
    # # print("MESSAGE: ", file_contents)  # Content
    # # print("\n")
    # # print("RECEIVERS: ", recp_list)  # Receivers
    # message = wa_automation(recp_list, file_contents, content_pic_vid)
    # print(message)
    app.run(host='0.0.0.0', port=5001)
