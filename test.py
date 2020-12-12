from tkinter import *
import tkinter
import tkinter.messagebox
from PIL import ImageTk, Image
from pyswip import *
from tkinter import simpledialog
import pylcs
import numpy as np



class DPDP():

    def __init__(self, master):

        frame = Frame(master)
        frame.grid()

        # attributes for colors
        self.tl_bg = "#EEEEEE"
        self.tl_bg2 = "#EEEEEE"
        self.tl_fg = "black"
        self.font = "Verdana 10"

        self.chatWindow = Label(master, bd=1, bg='white', width = 100, height = 8, justify="left")
        self.chatWindow.place(x=6,y=6,height=385,width=800)

        self.Button = Button(master, text="send", bg='blue',activebackground='light blue',width=12, height=5, command=lambda: queryGenerator())
        self.Button.place(x=6,y=400,height=88,width=120)


prolog = Prolog()  # Global handle to interpreter
prolog.consult('kb.pl')

retractall = Functor("retractall")
known = Functor("known", 3)


def write_py(X):
    """Prints the input X to the console and returns True to Prolog"""
    print(f'\t{X}')
    app.chatWindow['text'] += f'\t{X}\n'
    return True


def read_py(A: Atom, V: Atom, Y: Variable) -> bool:
    """
    Asks a question to the user and sends the response to Prolog.
    It is used to get Yes, No questions.
    Yes is normally evaluated by Prolog as True and any other input as False.

    :param A: The question (askable) that the usere should be prompted with.
    :param V: The value that the user needs to agree (yes) or disagree (any other input) with.
    :param Y: The value that Prolog will match with as True. Normally it's 'Yes'.

    :returns True if Y is a Prolog Variable and False otherwise.
    """
    if isinstance(Y, Variable):
        app.chatWindow['text'] += str(A) + " " + str(V) + "?\n"
        response = simpledialog.askstring("Input", str(A) + " " + str(V) + "?",
                                          parent=root)

        Y.unify(response)
        return True
    else:
        return False


def read_py_menu(A: Atom, Y: Variable, MenuList: list) -> bool:
    """
    Asks the user for input based on a menu. Choosing the index of the option
    as well as the exact text of the option would work. When the response
    has the best LCS match with an option above 10% it is the default response.

    :param A: The prompt (askable) the user needs to answer.
    :param V: The answer that the user would let Prolog know about.
    :param MenuList: The options that the user has to choose from.

    :returns True if Y is a Prolog variable and False otherwise.
    """
    if isinstance(Y, Variable):
        print(A)
        list_for_lcs = []
        question = "" + str(A) + "\n"
        for i, x in enumerate(MenuList):
            question += str(i) + " .  " + str(x) + "\n"
            list_for_lcs.append(str(x))

        response = get_menu_input(question, MenuList, list_for_lcs)
        app.chatWindow['text'] += f"YOU: {response}\n"
        print(f'\tYou chose {response}\n')
        Y.unify(response)
        return True
    else:
        return False


def get_menu_input(question: str, MenuList: list, lst_lcs: list) -> str:
    """
    Carries out the logic of identifying the choice of the user from the menu.
    A user can either choose a number or write some text.
    If they choose a number it has to be a valid number amoung the count of options given.
    If they provide a string it has to have the best match (among the options) be more than 10%.

    :param MenuList: The options that the user needs to choose from. They are stored as Prolog Atoms.
    :param lst_lcs: The options stored in a list of strings that Python can interprate.

    :returns a string of the option that the user chose.
    """
    app.chatWindow['text'] += f"SYSTEM: {question}"
    from_user = simpledialog.askstring("Input", question,
                                       parent=root)
    response_int = float('inf')
    try:
        response_int = int(from_user)
        response = str(MenuList[response_int])
    except:
        response = from_user.lower()
        response = most_appropriate(response, lst_lcs)
    return response


def most_appropriate(response: str, lst_lcs: list) -> str:
    """
    Choose the most appropriate option given the response string.
    It matches the choice by finding out the percentage LCS (Least Common Subsequence match).
    If the best match is above 30%, it is taken as the choice of the user.
    Otherwise the user will be reprompted for another option.

    :parm response: The input from the user.
    :param lst_lcs: The options stored in a list of strings that Python can interprate.

    :returns a string of the option that the user chose.
    """
    lcs = pylcs.lcs_of_list(response, lst_lcs)

    lengths = []
    for option in lst_lcs:
        lengths.append(len(option))

    # Calculate the percentage match of the LCS
    similarities = np.array(lcs)/np.array(lengths)

    # Identify the index of the highest match
    option_idx = np.argmax(similarities)

    # If the highest match is less than 10% return original response
    # so that the user can be reprompted
    # otherwise return the best option
    if similarities[option_idx] < 0.1:
        return response
    return lst_lcs[option_idx]


write_py.arity = 1
read_py.arity = 3

read_py_menu.arity = 3

registerForeign(read_py)
registerForeign(write_py)
registerForeign(read_py_menu)


def queryGenerator():
      # this prints the values that are chosen,correctly

    call(retractall(known))

    q = list(prolog.query("answer(X).", maxresult=1))  # prolog query
   # for e in q[0].values():
   # print("You have " + e)
   # break
    print(q)
    for v in q:
        print(v)
        print(v['X'])
        app.chatWindow['text'] += f"ANSWER: {str(v['X'])}\n"


root = Tk()
root.geometry("820x600")
root.resizable(0, 0)
root.config(bg='#44689E')
app = DPDP(root)
root.title("DPDP")
root.mainloop()
