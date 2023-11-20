import csv
import os

from flask import app

def getFromCSV(csv_file_path, value, key_heading, value_heading):
    # Replace 'your_csv_file.csv' with the path to your CSV file

    # The value you want to search for in the "NO." column
    target_value = value  # Change this to the value you want to search for

    # Open the CSV file for reading
    with open(csv_file_path, mode='r', newline='') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        amount = 0
        
        # Iterate through each row in the CSV
        for row in csv_reader:
            if row[key_heading] == target_value:
                # Found the matching row; get the amount from the same line
                amount = row[value_heading]
                print(f"Found NO. {target_value} with Amount: {amount}")
                break
        else:
            # This block will execute if the loop completes without finding the target_value
            print(f"NO. {target_value} not found in the CSV.")

        return amount
    
def getroomtotals(csv_file_path):
    print("IN A GET ROOM TOTAL")
    with open(csv_file_path, mode='r', newline='') as csv_file:
        csv_reader = csv.DictReader(csv_file)

        roomnumbers = []

        for row in csv_reader:
            if row.get('NO.'):
                roomNumber = row['NO.']
                roomnumbers.append(roomNumber)
        
        recurring_dict = {}
        for item in roomnumbers:
            # Check if the item is already in the dictionary
            if item in recurring_dict:
                # If it's in the dictionary, increment its count
                recurring_dict[item] += 1
            else:
                # If it's not in the dictionary, add it with a count of 1
                recurring_dict[item] = 1

        print("-----item------")
        print(recurring_dict)
        print(csv_reader)

        return recurring_dict
    

def convertToNumber(string):
    print(f'Attempting to convert {string} to a float')

    string = string.replace(',','')

    print(string)
    print(type(string))

    # newstring = int(string)
    # print(newstring, type(newstring))

    newstring = float(string)
    print(newstring, type(newstring))
    
    # print("Converting from ",type(string), " to ", type(newstring))
    return newstring
    

def remove_duplicate_rooms(data):
    seen_room_ids = set()
    unique_entries = []

    for entry in data:
        room_id = entry.get("RoomId")

        if room_id not in seen_room_ids:
            seen_room_ids.add(room_id)
            unique_entries.append(entry)

    return unique_entries

def createRooms(csv_file_path, writepath, listing):
    with open(csv_file_path, mode='r', newline='') as csv_file:
        # Create a CSV reader with a dictionary interface
        csv_reader = csv.DictReader(csv_file)
        data = []
       
        for row in csv_reader:
            print("row")
            print(row)

            roomtally = getroomtotals(csv_file_path)

            if row.get('NO.'):
                roomName = row.get('NO.')
                bedsAvailable = roomtally[row["NO."]]
                block = roomName[0]
                roomId=roomName.replace(block, '')

                studentName = row["NAME OF STUDENT"].strip()

                if studentName == "VACANT" or studentName == "vacant":
                    vacancystatus = True
                else:
                    vacancystatus = False

                print(row)

                finalCSV = {
                    "Name":roomName,
                    "Beds Available":bedsAvailable,
                    "Block":block,
                    "RoomId":roomId,
                    "fullAmount":row[" ROOM PRICE "],
                    "Super Listing":listing.slug,
                    "Listing Id":listing.id,
                    "Price per bed":row[" ROOM PRICE "], #✅
                    "Price":row[" ROOM PRICE "], #✅
                    "Beds Taken":0,
                    "Size":"size",
                    "Listing Id":listing.id,
                    "Vacancy Status":vacancystatus,
                    "Location":None
                }
                print(finalCSV)

                data.append(finalCSV)
               
                print("finalCSV")


         # CALCULATES THE NUMBER OF TIMES A ROOM APPEARS, AND DOES A TALLY.
        filtered_data = remove_duplicate_rooms(data)
        print("--------filtered_data-------")
        print(filtered_data)

        print("----- DATA FROM ROOM TALLY --------")
        print(roomtally)

        with open(writepath, mode='w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            print("------ROW DATA------")
            rowheader = [ "Name", "Beds Available", "Beds Taken", "Block", "RoomId", "Super Listing", "ListingId", "fullAmount",  "Location", "Size", "Vacancy Status", "Price per bed", "Price", "Listing Id"]
            csv_writer.writerow(rowheader)
            
            for item in filtered_data:
                print(item)
                row = [item["Name"], item["Beds Available"], item["Beds Taken"], item["Block"], item["RoomId"], item["Super Listing"], item["Listing Id"], convertToNumber(item["fullAmount"]), item["Location"], item["Size"],  item["Vacancy Status"], convertToNumber(item["Price per bed"]), convertToNumber(item["Price"]), item["Listing Id"] ]
                csv_writer.writerow(row)

    return writepath

      
def getroomstally(dataArray):
    
    recurring_dict = {}
    for item in dataArray:
        # Check if the item is already in the dictionary
        if item in recurring_dict:
            # If it's in the dictionary, increment its count
            recurring_dict[item] += 1
        else:
            # If it's not in the dictionary, add it with a count of 1
            recurring_dict[item] = 1

    print("-----item------")
    print(recurring_dict)
    # print(csv_reader)

    return recurring_dict
    

# def createRooms(csv_file_path, writepath, listing):
#     with open(csv_file_path, mode='r', newline='') as csv_file:
#         # Create a CSV reader with a dictionary interface
#         csv_reader = csv.DictReader(csv_file)
#         data = []
       
#         # CALCULATES THE NUMBER OF TIMES A ROOM APPEARS, AND DOES A TALLY.
#         roomtally = getroomtotals(csv_file_path)
#         print("----- DATA FROM ROOM TALLY --------")
#         print(roomtally)

#         for row in roomtally:
#             print("row")
#             print(row)

#             if row.get('NO.'):
#                 roomName = row.get('NO.')
#                 bedsAvailable = roomtally[row["NO."]]
#                 block = roomName[0]
#                 roomId=block.replace(block, '')

#                 studentName = row["NAME OF STUDENT"].strip()

#                 if studentName == "VACANT" or studentName == "vacant":
#                     vacancystatus = True
#                 else:
#                     vacancystatus = False
                
#                 finalCSV = {
#                     "Name":roomName,
#                     "Beds Available":bedsAvailable,
#                     "Block":block,
#                     "RoomId":roomId,
#                     "fullAmount":row["Room Price"],
#                     "Super Listing":listing.slug,
#                     "Listing Id":listing.id,
#                     "Price per bed":row["Price Per Bed"], #✅
#                     "Price":row["Room Price"], #✅
#                     "Beds Taken":0,
#                     "Size":"size",
#                     "Listing Id":listing.id,
#                     "Vacancy Status":vacancystatus,
#                     "Location":"CENTRAL UNIVERSITY"
#                 }

#                 data.append(finalCSV)

#                 print("finalCSV")
#                 print(finalCSV)

#         with open(writepath, mode='w', newline='') as csv_file:
#             csv_writer = csv.writer(csv_file)
#             print("------ROW DATA------")
#             rowheader = [ "Name", "Beds Available", "Beds Taken", "Block", "RoomId", "Super Listing", "listingId", "fullAmount",  "Location", "Size", "Vacancy Status", "Price per bed", "Price", "Listing Id"]
#             csv_writer.writerow(rowheader)

#             # 2 laptops and a white board
            
#             for item in data:
#                 print(item)
                
#                 # amount = getFromCSV(csv_file_path, item["Name"], "NO.", "AMOUNT")
                
#                 # bedsAvailable = roomtally[]
#                 # roomcount = minus the tenant from the total number of bedsAvailable 

#                 row = [item["Name"], item["Beds Available"], item["Beds Taken"], item["Block"], item["RoomId"], item["Super Listing"], item["listingId"], item["fullAmount"], item["Location"], item["Size"],  item["Vacancy Status"], item["Price per bed"], item["Price"], item["Listing Id"] ]
#                 csv_writer.writerow(row)

#     return writepath


# To find vacant rooms:
# if name of student starts with vacant  == vacant
# append room number to an array
# and then do the math from there 👍


def getOccupants(csv_file_path, listing):
    with open(csv_file_path, mode='r', newline='') as csv_file:
        # Create a CSV reader with a dictionary interface
        csv_reader = csv.DictReader(csv_file)
        filename = f'{listing.slug}-newdata.csv'

        
        with open(filename, mode='w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)

                # user = User(username = row["Name"], password = "0000",email = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')+row["Number"]+"@prestoghana.com", phone = row["Number"], indexNumber=row["Index Number"], listing=row["Listing"], paid=row["Paid"], roomNumber=row["Room Number"], fullAmount=row["Full Amount"], balance=row["Balance"], listingSlug=row["listingSlug"] )


            header = ["Name","Number","Index Number","Full Amount","Paid","Balance","Room Number","Listing", "listingSlug"]
            csv_writer.writerow(header)


            for row in csv_reader:
                print(row)
                if row.get('NO.'):
                    student = row['NAME OF STUDENT']
                    balance = row[' BALANCE ']
                    fullamount = row[' ROOM PRICE ']
                    paid = row[' PAID ']
                    number = row['TEL NO.']
                    indexNumber = row['REG. NUMBER']
                    roomNumber = row['NO.']
                    course = row['PROGRAMME']
                    level = row['NO.']

                    row = [ student,number, indexNumber, fullamount, paid, balance, roomNumber, listing.slug, listing.slug ]
                    csv_writer.writerow(row)
                    
    return filename
