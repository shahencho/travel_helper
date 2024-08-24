import gspread
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# Google Sheets setup
gs = gspread.service_account(filename='credentials.json')
sh = gs.open_by_key('1A7mr9MAA1gomAwOv3NeoVhIPAYOgf1mv3fxTlbcQjf4')
wks = sh.get_worksheet(0)

# Define expected headers
expected_headers = [
    'id', 'Agency_Name', 'Country', 'City_Town', 'Hotel_Name', 
    'Hotel_Rating_Stars', 'Available_Dates_To_Fly', 'Available_Return_Dates', 'Total_Price', 'How_Many_Nights'
]

# Print the headers from the Google Sheet
actual_headers = wks.row_values(1)
print("Actual Headers:", actual_headers)

# Telegram bot setup
TOKEN = '7256193277:AAEMtDw3bqG8DgImbcR0Y4w8Znq39NatknA'  # Replace with your bot's token

# Define a dictionary to track user selections
user_selections = {}

# Helper function to parse date range from selection
def parse_date_range(selection):
    month_map = {
        'Sep': (9, 2024),
        'Oct': (10, 2024),
        'Nov': (11, 2024),
        'Dec': (12, 2024),
        'Jan': (1, 2025),
        'Feb': (2, 2025),
        'Mar': (3, 2025)
    }
    parts = selection.split('_')
    if len(parts) == 2:
        month_year = parts[1]
        if month_year in month_map:
            month, year = month_map[month_year]
            start_date = datetime(year, month, 1)
            end_date = datetime(year, month + 1, 1) if month < 12 else datetime(year + 1, 1, 1)
            return start_date, end_date
    return None, None

async def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("🇪🇬 Egypt: Sharm El Sheikh", callback_data='1')],
        [InlineKeyboardButton("🇪🇬 Egypt: Hurgada", callback_data='2')],
        [InlineKeyboardButton("🇹🇳 Tunis", callback_data='3')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Hi, I am a bot that will help you to find hot deals. "
        "Please share a few important things that you want me to help you with.\n"
        "What country are you looking for?",
        reply_markup=reply_markup
    )

async def button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    country = ""
    if query.data == '1':
        country = "Egypt: Sharm El Sheikh"
    elif query.data == '2':
        country = "Egypt: Hurgada"
    elif query.data == '3':
        country = "Tunis"

    print(f"Button selection of Country -> : {country} and query.data is {query.data}")

    # Store the country selection for the user
    user_id = query.from_user.id
    user_selections[user_id] = {"country": country, "nights": None, "date_range": None}

    # Proceed to nights selection
    await query.edit_message_text(
        text="Please select the number of nights you want to spend in:\n🌍 " + country,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("6", callback_data=f'{query.data}_6')],
            [InlineKeyboardButton("8", callback_data=f'{query.data}_8')],
            [InlineKeyboardButton("10", callback_data=f'{query.data}_10')]
        ])
    )

async def night_selection(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    # Split the callback data
    data = query.data.split('_')
    country = ""
    if data[0] == '1':
        country = "Egypt: Sharm El Sheikh"
    elif data[0] == '2':
        country = "Egypt: Hurgada"
    elif data[0] == '3':
        country = "Tunis"

    print(f"Function [night_selection] data is -> : {data} and selected country is {country}")

    # Store the user's night selection
    user_id = query.from_user.id
    user_selections[user_id]["country"] = country
    user_selections[user_id]["nights"] = data[1]

    # Proceed to date selection
    await query.edit_message_text(
        text=f"You chose \n🌍 <b>Country:</b> {country}\n🌙 <b>Nights:</b> {data[1]}\n\nPlease select your preferred date range:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Sep 2024", callback_data=f'{data[0]}_{data[1]}_2024_Sep')],
            [InlineKeyboardButton("Oct 2024", callback_data=f'{data[0]}_{data[1]}_2024_Oct')],
            [InlineKeyboardButton("Nov 2024", callback_data=f'{data[0]}_{data[1]}_2024_Nov')],
            [InlineKeyboardButton("Dec 2024", callback_data=f'{data[0]}_{data[1]}_2024_Dec')],
            [InlineKeyboardButton("Jan 2025", callback_data=f'{data[0]}_{data[1]}_2025_Jan')],
            [InlineKeyboardButton("Feb 2025", callback_data=f'{data[0]}_{data[1]}_2025_Feb')],
            [InlineKeyboardButton("Mar 2025", callback_data=f'{data[0]}_{data[1]}_2025_Mar')],
            [InlineKeyboardButton("Any", callback_data=f'{data[0]}_{data[1]}_any')]
        ]),
        parse_mode='HTML'
    )

from datetime import datetime

async def date_selection(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    # Split the callback data
    data = query.data.split('_')

    print(f"Function [date_selection] data is -> : {data}")

    # Initialize variables
    country = ""
    nights = None
    date_range = None
    start_date, end_date = None, None

    # Retrieve user's selections
    user_id = query.from_user.id
    user_selection = user_selections.get(user_id, {"country": None, "nights": None, "date_range": None})

    # Determine country based on data[0]
    if len(data) >= 2:
        if data[0] == '1':
            country = "Egypt: Sharm El Sheikh"
        elif data[0] == '2':
            country = "Egypt: Hurgada"
        elif data[0] == '3':
            country = "Tunis"

    # Determine nights and date range
    if len(data) >= 3:
        nights = data[1]
        date_range = data[2]
        if len(data) == 4:
            date_range += f"_{data[3]}"
    else:
        await query.edit_message_text(
            text="🚫 Invalid selection. Please try again.",
            parse_mode='HTML'
        )
        return

    # Update the user's selection
    user_selection["country"] = country
    user_selection["nights"] = nights
    user_selection["date_range"] = date_range
    user_selections[user_id] = user_selection

    # Provide feedback on current selection
    current_selection = (
        f"Current Selection:\n"
        f"🌍 <b>Country:</b> {user_selection['country']}\n"
        f"🌙 <b>Nights:</b> {user_selection['nights']}\n"
        f"📅 <b>Date Range:</b> {user_selection['date_range']}\n\n"
    )

    # Handle 'any' date range case
    if date_range == 'any':
        start_date, end_date = None, None
    else:
        start_date, end_date = parse_date_range(date_range)

    if date_range != 'any' and (start_date is None or end_date is None):
        response = f"{current_selection}🚫 Invalid date range selected. Please try again."
        keyboard = [[InlineKeyboardButton("Back to Main Menu", callback_data='back_to_main')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text=response,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        return

    # Debugging: Output the current selection
    print(current_selection)

    # Static data for testing
    # records = [
    #     {
    #         'id': '20',
    #         'Agency_Name': 'Anriva',
    #         'Country': 'Egypt: Sharm El Sheikh',
    #         'City_Town': 'Monastir',
    #         'Hotel_Name': 'Mediterranee Thalasso Golf',
    #         'Hotel_Rating_Stars': '***',
    #         'Available_Dates_To_Fly': '09/06/2024',
    #         'Available_Return_Dates': '09/16/2024',
    #         'Total_Price': '$2,362',
    #         'How_Many_Nights': '8'
    #     },
    #     {
    #         'id': '21',
    #         'Agency_Name': 'Anriva',
    #         'Country': 'Egypt: Sharm El Sheikh',
    #         'City_Town': 'Monastir',
    #         'Hotel_Name': 'Mediterranee Thalasso Golf',
    #         'Hotel_Rating_Stars': '***',
    #         'Available_Dates_To_Fly': '09/13/2024',
    #         'Available_Return_Dates': '09/23/2024',
    #         'Total_Price': '$2,362',
    #         'How_Many_Nights': '8'
    #     }
    # ]

    # Read data from Google Sheet based on the selection
    records = wks.get_all_records(expected_headers=expected_headers)
    print(f"[DEBUG] Filtering for Country: {country}, Nights: {nights}, Date Range: {date_range}")
    
    found_records = []
    for record in records:
        try:
            available_dates_to_fly = datetime.strptime(record["Available_Dates_To_Fly"], '%m/%d/%Y')
            available_return_dates = datetime.strptime(record["Available_Return_Dates"], '%m/%d/%Y')

            # Debug print statements
            print(f"Checking record: {record}")
            print(f"Available Dates To Fly: {available_dates_to_fly}, Available Return Dates: {available_return_dates}")
            print(f"Date Range Start: {start_date}, End: {end_date}")

            # Check if the available dates fall within the selected range
            date_in_range = (start_date is None or end_date is None) or (start_date <= available_return_dates and end_date >= available_dates_to_fly)
            print(f"Date in range: {date_in_range}")

            # Additional debug to ensure matching country and nights
            record_country_match = record["Country"].strip() == country
            record_nights_match = str(record["How_Many_Nights"]) == nights
            print(f"Country match: {record_country_match}, Nights match: {record_nights_match}")

            if date_in_range and record_country_match and record_nights_match:
                found_records.append(record)
                print("Record added:", record)  # Debugging
        except ValueError as e:
            print(f"[DEBUG] Date parsing error: {e}")

    print(f"Found records in static data - after search: {found_records}")

    if found_records:
        response = f"{current_selection}We found some great hot deals for you:\n\n"
        for record in found_records:
            response += (
                f"🔥 <b>HOT DEAL FROM AGENCY:</b> <b>{record['Agency_Name']}</b>\n"
                f"📍 <b>City/Town:</b> {record['City_Town']}\n"
                f"🏨 <b>Hotel Name:</b> {record['Hotel_Name']}\n"
                f"⭐ <b>Hotel Rating:</b> {record['Hotel_Rating_Stars']}\n"
                f"✈️ <b>Available Dates to Fly:</b> {record['Available_Dates_To_Fly']}\n"
                f"🏠 <b>Available Return Dates:</b> {record['Available_Return_Dates']}\n"
                f"💲 <b>Total Price:</b> {record['Total_Price']}\n\n"
            )
        response += (
            "📞 If any of these deals look good to you, please contact the respective agency for more details.\n"
            "🔄 If you want to search for more deals or choose another country, simply select from the options below."
        )
    else:
        response = (
            f"{current_selection}🚫 Sorry, no hot deals were found for the selected options. Please try different criteria or choose another country.\n\n"
            "🔙 You can go back to the main menu and start a new search."
        )

    keyboard = [
        [InlineKeyboardButton("Back to Main Menu", callback_data='back_to_main')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=response,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )




async def handle_back_to_main(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    # Ensure we are using the correct method to send the response
    chat_id = query.message.chat_id
    await context.bot.send_message(
        chat_id=chat_id,
        text="Hi, I am a bot that will help you to find hot deals. "
             "Please share a few important things that you want me to help you with.\n"
             "What country are you looking for?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🇪🇬 Egypt: Sharm El Sheikh", callback_data='1')],
            [InlineKeyboardButton("🇪🇬 Egypt: Hurgada", callback_data='2')],
            [InlineKeyboardButton("🇹🇳 Tunis", callback_data='3')]
        ])
    )

async def handle_text_input(update: Update, context: CallbackContext):
    # Respond to any text input with a prompt to select from the buttons
    keyboard = [
        [InlineKeyboardButton("🇪🇬 Egypt: Sharm El Sheikh", callback_data='1')],
        [InlineKeyboardButton("🇪🇬 Hurgada", callback_data='2')],
        [InlineKeyboardButton("🇹🇳 Tunis", callback_data='3')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Hey, please choose one of the given countries by clicking on the options below:",
        reply_markup=reply_markup
    )

async def debug_callback_data(update: Update, context: CallbackContext):
    query = update.callback_query
    print(f"[DEBUG] Global handler: Received callback data: {query.data}")

# Define main function to run the bot
def main():
    # Create the application
    app = ApplicationBuilder().token(TOKEN).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button, pattern='^[1-3]$'))
    app.add_handler(CallbackQueryHandler(night_selection, pattern='^[1-3]_(6|8|10)$'))
    app.add_handler(CallbackQueryHandler(date_selection, pattern='^[1-3]_(6|8|10)_(2024|2025)_(Sep|Oct|Nov|Dec|Jan|Feb|Mar|any)$'))
    app.add_handler(CallbackQueryHandler(date_selection, pattern='^[1-3]_(6|8|10)_any$'))
    app.add_handler(CallbackQueryHandler(handle_back_to_main, pattern='^back_to_main$'))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input))
    app.add_handler(CallbackQueryHandler(debug_callback_data))
    # Run the bot
    app.run_polling()

if __name__ == '__main__':
    main()
