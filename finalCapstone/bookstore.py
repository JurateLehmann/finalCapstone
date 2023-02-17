# NOTE for reviewwer: uploading only .py file as it supposed to create db file. 

import sqlite3
from tabulate import tabulate


# To output some messages in color: 
class bcolors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

#___________________________________________________________FUNCTION DEFINITION SECTION:____________________________________________________________________ 

# This outputs in table format. Please note headers are intended only for 'books' table:

def table_output(source):
    return tabulate(source, headers =('id','Title','Author', 'Qty'),tablefmt='grid')

# The following asks user to input title, author, and quantity and adds entry into the table with auto-generated id.
# There are built in checks: it repeatedly asks user to enter a value in case entry is left blank (so to ensure all attributes have values).  
# 'Quantity' entry has an additional checks: ValueError and quantity >=0  to ensure user adds either a 0 or a positive integer.
# User can abort entry at any point by entering '-1', which then returns to Main menu. 

def capturing_book():
    while True: 
        title_entry = input("Please enter book TITLE or '-1' to return to 'Main Menu': ")
        if title_entry == "-1":
            print("No changes to the table. Book entry aborted as chose to return to Main Menu.")
            return
        elif title_entry != "":
            break
        else: 
            print(bcolors.FAIL + """Error: TITLE field cannot be left blank. Please try again.""" + bcolors.ENDC)
    while True: 
        author_entry = input("Please enter AUTHOR of the book or enter '-1' to return to 'Main Menu': ")
        if author_entry == "-1":
            print("No changes to the table. Book entry aborted as chose to return to Main Menu.")
            return
        elif author_entry != "":
            break     
        else: 
            print(bcolors.FAIL + """Error: AUTHOR field cannot be left blank. Please try again.""" + bcolors.ENDC)
    while True:
        try: 
            qty_entry = int(input("Please enter QUANTITY of copies in stock or '-1' to return to 'Main Menu': "))
            if qty_entry >= 0:
                new_book = [title_entry,author_entry, qty_entry]
                cursor.execute(''' INSERT INTO books(Title, Author, Qty) VALUES(?,?,?)''', new_book)
                db.commit
                print(bcolors.OKGREEN + "\nSuccess!" + bcolors.ENDC)
                cursor.execute('''SELECT * FROM books WHERE Title = ? AND Author = ? AND Qty = ?''',(new_book))
                print(f"The following entry has been added to the table: \n{table_output(cursor.fetchall())}")
                break
            elif qty_entry < 0 and qty_entry != -1:
                print(bcolors.FAIL +"Error: QUANTITY has to be a positive integer. Please try again." + bcolors.ENDC)
            elif qty_entry == -1:
                print("No changes to the table. Book entry aborted as chose to return to Main Menu.")
                return
        except ValueError:
            print(bcolors.FAIL +"Error: QUANTITY has to be an integer. Please try again." + bcolors.ENDC)
            pass
        
    
# The following asks user to enter id of book which needs updating, then it displays record user is updating 
# and prompts user to update each attribute or to enter '0' for attributes to remain unchanged. 
# NB: In order to keep process clean, once id is entered, there is no option to return to Main Menu as user can enter all '0's to keep record unchanged. 
# But user can entere '0' instead of id, to return to Main Menu. There are checks agains NULL value fields, and to ensure qty entry is an integer. 
# Quantity updating asks for quantity DIFFERENCE instead of new total quantity. This is in mind for restocking to make it user friendly. 
# NOTE: quantity adjustment does not have a check against total quantity going negative, because if sales overcommit there could be cases of books being on back order. 
# (If anything a check for negative total quantity should be built in sales commitment tables, which is not part of this task.)

def update_book():
    while True:
            book_id = input("Please enter ID of the book you would like to update or '0' to return to the main menu: ")
            if book_id == "0":
                break
            else:
                cursor.execute('''SELECT * FROM books WHERE id = ?''', (book_id,))
                book_to_update = cursor.fetchall()  
                if book_to_update == []:
                    print(bcolors.FAIL +f"""Error: there is no record with id '{book_id}'. 
Note: if id unknown records can be searched by title and/or author via Main Menu option 4. Please try again.""" + bcolors.ENDC)
                    pass
                else: 
                    print (f"The following record is being updated:\n{table_output(book_to_update)}\n")
                    updated_entry = []
                    while True:
                        new_title = input ("Please enter NEW TITLE or '0' if title stays the same: ")
                        if new_title == "0":
                            updated_entry.append(book_to_update[0][1])
                            break
                        elif new_title !="": 
                            updated_entry.append(new_title)
                            break
                        else:
                            print(bcolors.FAIL + """Error: TITLE field cannot be left blank. Please try again.""" + bcolors.ENDC)

                    while True:    
                        new_author = input ("Please enter NEW AUTHOR or '0' if author stays the same: ")
                        if new_author == "0":
                            updated_entry.append(book_to_update[0][2])
                            break
                        elif new_author != "":
                            updated_entry.append(new_author)
                            break
                        else: 
                            print(bcolors.FAIL + """Error: AUTHOR field cannot be left blank. Please try again.""" + bcolors.ENDC)

                    while True:
                        try:
                            new_qty = int(input ("""Please enter '0' if quantity remains unchanged or enter DIFFERENCE to ADD/SUBTRACT from stock
(ex. if want to add 5 enter 5):   """))  
                            
                            break
                        except ValueError:
                            print(bcolors.FAIL +"Error: quantity DIFFERENCE should be integer. Please try again." + bcolors.ENDC)
                        
                    updated_entry.append(book_to_update[0][3] + new_qty)
                    updated_entry.append(book_id)
                    
                    cursor.execute('''UPDATE books SET Title = ?, Author = ?, Qty = ? WHERE id =?''',(updated_entry),)
                    db.commit()
                    cursor.execute('''SELECT * FROM books WHERE id = ?''', (book_id,))
                    print(bcolors.OKGREEN + "\nSuccess!" + bcolors.ENDC)
                    print(f"Record after updates:\n{table_output(cursor.fetchall())}\n")

# The following asks user to enter id (or '-1' to return to main menu). If entered id matches one on record it displays output in warning format that user is about to delete. 
# User needs to confirm deletion by entering 'y' or press any other key to cancel. 
# Confirmation message is then displayed. 


def delete_book():
    while True: 
        delete_id = input("Please enter book id to delete record or enter '-1' to return to main menu: ")  
        if delete_id == "-1":
            break   
        else: 
            cursor.execute('''SELECT * FROM books WHERE id = ?''',(delete_id,))
            search_results = cursor.fetchall()
            if search_results == []:
                print(bcolors.FAIL +f"""Error: there is no record with id '{delete_id}'. 
Note: if id unknown records can be searched by title and/or author via Main Menu option 4. Please try again.""" + bcolors.ENDC)
                pass
            else: 
                print(bcolors.WARNING + "You are about to delete the following entry:")
                print(table_output(search_results))

                delete_confirmamtion = input("Please confirm by entering 'Y' if to proceed deleting or press any other key to abort: "+ bcolors.ENDC)
                if delete_confirmamtion.lower() == "y":
                    cursor.execute('''DELETE FROM books WHERE id = ?''', (delete_id,))
                    db.commit
                    print(bcolors.OKGREEN + "\nSuccess!" + bcolors.ENDC)
                    print("Entry has been deleted.")
                else: 
                    print(f"Deletion aborted: id '{delete_id}' left on record.")

# The following gives flexible search options: 
    # 1. by title/author - asks user to input as much criteria as user chooses: ex. it can be exact attribute value, or a word/part word, or left blank if not searching by attritbute in question. 
    # 2. quantity - asks user to define range of search by entering bounds: lower and upper, ex. lower '0' and upper '150' will return all records with quantities >= 0 and <= 150
    # 3. id same as quantity asks user to define range of id. It can be used to search the most recent entries or to display full table if bounds set wide enough. 

# As per normal there are checks for input values: quantity and id bound inputs have to have integer inputs or error message is displayed. 
# User is notified if search does not return any results, otherwise, results returned in table grid format. 

def search_books():
    while True: 
        search_criteria = input("""\n\tSEARCH options:
1. by TITLE and/or AUTHOR
2. by range of QUANTITY 
3. by range of ID (wide range = entire table)

Please enter correcponding number (ex. enter 1 to search by title and/or author) or '-1' to return to Main Menu: """)
        if search_criteria == "-1":
            break
        elif search_criteria == "1":
            search_title = input("Please enter a TITLE or a word from title to search (leave blank if not searching by title): ")
            search_author = input("Please enter an AUTHOR or part name of an author to search (leave blank if not searching by author): ")
            cursor.execute('''SELECT * FROM books WHERE title LIKE '%' || ? || '%' AND author LIKE '%' || ? || '%' ''', (search_title, search_author,))
            search_results = cursor.fetchall()
            if search_results == []:
                print(bcolors.WARNING + "Sorry, but entered criteria did not return any records. Please double check or enter different criteria to try again." + bcolors.ENDC)
                pass

            else: 
                print("\nSearch results: ")
                print(table_output(search_results))
        elif search_criteria == "2":
            print("""\nLet's define range. 0 to 150 would be entered '0' for lower and '150' for upper bound.""")
            while True: 
                try: 
                    qty_lower_bound = int(input("Please enter LOWER bound: "))
                    if qty_lower_bound !="":
                        break
                    else:
                        print(bcolors.FAIL + "Error: bound has to be an integer. Please try again." + bcolors.ENDC)
                except ValueError:
                    print(bcolors.FAIL + "Error: bound has to be an integer. Please try again." + bcolors.ENDC)
            while True: 
                try: 
                    qty_upper_bound = int(input("Please enter UPPER bound: "))
                    if qty_upper_bound !="":
                        break
                    else:
                        print(bcolors.FAIL + "Error: bound has to be an integer. Please try again." + bcolors.ENDC)
                except ValueError:
                    print(bcolors.FAIL + "Error: bound has to be an integer. Please try again." + bcolors.ENDC)
            
            cursor.execute('''SELECT * FROM books WHERE Qty between ? and ? order by Qty ''', (qty_lower_bound,qty_upper_bound,))
            search_results = cursor.fetchall()
            if search_results == []:
                print(bcolors.WARNING + "Sorry, but entered criteria did not return any records. Please double check or enter different criteria to try again." + bcolors.ENDC)
                pass

            else: 
                print("\nSearch results: ")
                print(table_output(search_results))
        elif search_criteria == "3":
            print("""\nLet's define id range. 0 to 10000 would be entered '0' for lower and '10000' for upper bound.""")
            while True: 
                try: 
                    id_lower_bound = int(input("Please enter LOWER bound: "))
                    if id_lower_bound !="":
                        break
                    else:
                        print(bcolors.FAIL + "Error: bound has to be an integer. Please try again." + bcolors.ENDC)
                except ValueError:
                    print(bcolors.FAIL + "Error: bound has to be an integer. Please try again." + bcolors.ENDC)
            while True: 
                try: 
                    id_upper_bound = int(input("Please enter UPPER bound: "))
                    if id_upper_bound !="":
                        break
                    else:
                        print(bcolors.FAIL + "Error: bound has to be an integer. Please try again." + bcolors.ENDC)
                except ValueError:
                    print(bcolors.FAIL + "Error: bound has to be an integer. Please try again." + bcolors.ENDC)
            
            
            cursor.execute('''SELECT * FROM books WHERE id between ? and ? order by id ''', (id_lower_bound,id_upper_bound,))
            search_results = cursor.fetchall()
            if search_results == []:
                print("Sorry, but entered criteria did not return any records. Please double check or enter different criteria to try again.")
                pass
            else: 
                print("\nSearch results: ")
                print(table_output(search_results))
        else: 
            print(f"Afraid '{search_criteria}' is not on the menu. Please try again. ")

#######____________________________________________ CODE SECTION ________________________________________________________#########
            

db = sqlite3.connect('ebookstore_db')
cursor = db.cursor()


# If 'books' table does not exist yet, the following creates it and inserts first few rows into the table. 
try: 
    cursor.execute('''
    CREATE Table books(id INTEGER PRIMARY KEY NOT NULL, Title TEXT NOT NULL, Author TEXT NOT NULL, Qty INTEGER NOT NULL)''')
    db.commit()
    book_records = [
    (3001, 'A Tale of Two Cities', 'Charles Dickens', 30), 
    (3002, 'Harry Potter and the Philosopher\'s stone', 'J.K.Rowling', 40), 
    (3003, 'The Liion, the Witch and the Wardrobe', 'C.S. Lewis', 25), 
    (3004, 'The Lord of the Rings', 'J.R.R Tolkien', 37),
    (3005, 'Alice in Wonderland', 'Lewis Carroll', 12)
    ]
    cursor.executemany(''' INSERT INTO books(id, Title, Author, Qty) VALUES(?,?,?,?)''', book_records)
    db.commit()
except sqlite3.OperationalError: 
    pass


# The following ouputs existing 'books' table to console:
cursor.execute('''SELECT * FROM books''')
print(f"\n'books' table: \n{table_output(cursor.fetchall())}")

# User is presented with menu options: 
while True:
    main_menu = print(bcolors.BOLD + "\n\tMain Menu"+ bcolors.ENDC, """\n
1. Enter book
2. Update book
3. Delete book
4. Search books
0. Exit
""")

    user_choice = input("Please enter a corresponding number from the menu option (ex. 1): ")

# Depending on user's choice a correcponding function is run to carry out user's request. 
# If need to investigate, all functions are above in FUNCTION DEFINITION section. 
    if user_choice == "1":
        print("You are now adding new book entry. Please note all fields have to have values and quantity has to be a positive integer.")
        capturing_book()

    elif user_choice == "2":
        update_book()
    
    elif user_choice == "3":
        delete_book()
        
    elif user_choice == "4":
        search_books()
    
    elif user_choice == "0":
        print("\nMany thanks! You are logged off now. Hope to see you soon :)")
        exit()
    else:
        print(bcolors.FAIL + "Error: incorrect entry. Please try again."+ bcolors.ENDC)
                        