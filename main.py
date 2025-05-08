#Pascariu Alexandru Carlo
#grupa 152
# python 3.13.3 
import itertools, json, acceptor
from collections import defaultdict, deque

class Stare:

    _id_iter = itertools.count() # folosit pentru a număra stările (q0, q1, ...)

    def __init__(self, name=None):
        self.id = next(Stare._id_iter)
        self.name = f"q{self.id}" if name is None else name
        self.tranzitii = defaultdict(set)

class NFA:
    def __init__(self, start, final):
        self.start = start
        self.final = final # e de ajuns o singura stare datorita algoritmului lui Thompson
        self.stari = set()

    def add_stari(self, *stari):
        self.stari.update(stari)

class DFA:
    def __init__(self):
        self.stari = {}
        self.start = None
        self.stari_final = set()
        self.tranzitii = defaultdict(dict)

def concat(regex):
    output = ""
    for i in range(len(regex)):
        output += regex[i]
        if regex[i] in ")*+?" or regex[i].isalnum(): # daca caracterul curent este "operatie" sau litera..
            if i+1 < len(regex): # regex-ul nu e la final...
                if regex[i+1].isalnum() or regex[i+1] == '(': # si urmeaza litera sau grupare
                    output += '.'
    return output

def postfix(regex):
    # la baza sta algoritmul Shunting-Yard
    ordine = {'*': 3, '+': 3, '?': 3, '.': 2, '|': 1}
    output = ""
    operatori = []

    for c in regex:
        if c.isalnum(): # mereu punem literele in output direct
            output += c
        elif c == '(':
            operatori.append(c)
        elif c in "*+?.|":
            while operatori and operatori[-1] != '(' and ordine[operatori[-1]] >= ordine[c]: # punem intai operatiile cu prioritate mai mare
                output += operatori.pop()
            operatori.append(c)
        else: # scoatem operatorii ramasi din grupare
            while operatori and operatori[-1] != '(':
                output += operatori.pop()
            operatori.pop() # scoatem paranteza din stiva de operatori
        
    # punem operatorii ramasi
    while operatori:
        output += operatori.pop()
    return output

def build_nfa(postfix): # toate nfa-urile vor avea o singura stare finala
    stack = []
    for c in postfix:
        if c.isalnum(): # facem un nfa care ajunge din c in starea finala
            s0, s1 = Stare(), Stare()
            s0.tranzitii[c].add(s1)
            nfa = NFA(s0, s1)
            nfa.add_stari(s0, s1)
            stack.append(nfa)
        elif c in "*+?":
            nfa1 = stack.pop()
            s0, s1 = Stare(), Stare()
            if c == '*': # litera lambda ('') va merge din s0 la finalul noului nfa, cat si la inceputul nfa-ului anterior
                s0.tranzitii[''].update([nfa1.start, s1])
                nfa1.final.tranzitii[''].update([nfa1.start, s1]) # iar la finalul vechiului nfa putem merge inapoi sau mai departe
            elif c == '+': # lambda va merge neaparat la inceputul nfa-ului anterior pentru a garanta o aparitie
                s0.tranzitii[''].add(nfa1.start)
                nfa1.final.tranzitii[''].update([nfa1.start, s1])
            elif c == '?': # lambda va merge fie la inceputul nfa-ului anterior, fie la finalul noului nfa
                s0.tranzitii[''].update([nfa1.start, s1])
                nfa1.final.tranzitii[''].add(s1) 
            
            # adaugam totul intr-un nou nfa

            nfa = NFA(s0, s1)
            nfa.add_stari(s0, s1, *nfa1.stari)
            stack.append(nfa)
        elif c == '.': # lipim cele doua nfa-uri: starea initiala din nfa2 va fi starea finala a nfa1, iar nfa-ul rezultant va avea ca stare initiala st init din nfa1, si ca stare finala st final din nfa2
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            nfa1.final.tranzitii[''].add(nfa2.start)
            nfa = NFA(nfa1.start, nfa2.final)
            nfa.add_stari(*nfa1.stari, *nfa2.stari)
            stack.append(nfa)
        elif c == '|': # din lambda putem pleca in cele doua nfa-uri anterioare, care vor avea acelasi final
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            s0, s1 = Stare(), Stare()
            s0.tranzitii[''].update([nfa1.start, nfa2.start])
            nfa1.final.tranzitii[''].add(s1) # unim finalurile celor doua
            nfa2.final.tranzitii[''].add(s1)
            nfa = NFA(s0, s1)
            nfa.add_stari(s0, s1, *nfa1.stari, *nfa2.stari)
            stack.append(nfa)
    final_nfa = stack.pop() # rezultatul final va fi nfa-ul nostru 
    return final_nfa

def inchidere_lambda(stari): # toate starile in care putem ajunge doar prin lambda
    stack = list(stari)
    inchidere = set(stari)
    while stack:
        stare = stack.pop()
        for urm_stare in stare.tranzitii['']:
            if urm_stare not in inchidere:
                inchidere.add(urm_stare)
                stack.append(urm_stare)
    return inchidere

def mutari(stari, litera): # toate starile in care putem ajunge dintr-o litera
    result = set()
    for stare in stari:
        result.update(stare.tranzitii.get(litera, []))
    return result

def nfa_to_dfa(nfa):
    dfa = DFA()
    litere = {c for s in nfa.stari for c in s.tranzitii if c != ''}
    
    # formam set-uri de stari si le asociem intr-un map; incepem de la inchiderea lambda din starea initiala
    set_start = frozenset(inchidere_lambda([nfa.start]))
    stare_map = {set_start: "q0"}
    queue = deque([set_start])
    dfa.stari["q0"] = set_start
    dfa.start = "q0" # evident
    cnt = 1

    while queue: # facem cautare pe latime pe toate starile
        set_curent = queue.popleft()
        nume_curent = stare_map[set_curent]
        for l in litere:
            set_mutari = mutari(set_curent, l) # de unde putem pleca dintr-o litera?
            set_inchidere = frozenset(inchidere_lambda(set_mutari))
            
            if not set_inchidere: # mergem mai departe daca nu mai avem unde merge
                continue
            
            if set_inchidere not in stare_map:
                stare_map[set_inchidere] = f"q{cnt}"
                dfa.stari[f"q{cnt}"] = set_inchidere
                queue.append(set_inchidere) # se pare ca mai avem de cautat
                cnt += 1
            dfa.tranzitii[nume_curent][l] = stare_map[set_inchidere] # adaugam in dfa

    # adaugam starile finale din nfa in dfa
    for name, stari in dfa.stari.items():
        if nfa.final in stari:
            dfa.stari_final.add(name)

    return dfa, litere

def print_dfa(dfa, litere, fisier): # aici e mai plictisitor, nu prea are rost sa spun multe
    with open(fisier, "w") as f:
        print("Sigma:", file=f)
        for l in sorted(litere):
            print(l, file=f)
        print("End", file=f)
        print("States:", file=f)
        for stare in dfa.stari:
            atrib = []
            if stare == dfa.start:
                atrib.append("S")
            if stare in dfa.stari_final:
                atrib.append("F")
            if atrib:
                print(f"{stare}, {', '.join(atrib)}", file=f)
            else:
                print(stare, file=f)
        print("End", file=f)
        print("Transitions:", file=f)
        for src in dfa.tranzitii:
            for l, dst in dfa.tranzitii[src].items():
                print(f"{src}, {l}, {dst}", file=f)
        print("End", file=f)

with open("LFA-Assignment2_Regex_DFA_v2.json", "r") as f:
    regexes = json.load(f)
    for i in regexes:
        print(f"Suntem la regex-ul {i["name"]} ({i["regex"]})")
        
        regex = i["regex"]
        regex = concat(regex)
        regex = postfix(regex)
        nfa = build_nfa(regex)
        dfa, litere = nfa_to_dfa(nfa)
        
        # am transformat dfa-ul în format-ul de la tema 1 doar de dragul de a reutiliza cod anterior :))
        print_dfa(dfa, litere, i["name"])
        acceptor_dfa = {"alfabet": [], "stari": [], "tranzitii" : {}, "start": "", "final" : []} 
        
        if acceptor.validare(i["name"], acceptor_dfa) == 1:
            for w in i["test_strings"]:
                if acceptor.acceptare(w["input"], acceptor_dfa) == w["expected"]:
                    print(f"Cuvântul {w["input"]} este recunoscut corespunzător.")
                else:
                    print(f"Cuvântul {w["input"]} NU este recunoscut corespunzător!")
        else:
            print("DFA INCORECT")



