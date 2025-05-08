#Pascariu Alexandru Carlo
# grupa 152
# python 3.13.2
def validare(nume_fisier, dfa):
    with open(nume_fisier, "r") as f:
        stare = 0 # 1 sigma, 2 states, 3 transitions
        for line in f:
            l = line.strip()
        
            # ignore comments
            if l[0] == "#":
                continue
            match l:
                case "Sigma:":
                    stare = 1
                case "States:":
                    stare = 2
                case "Transitions:":
                    stare = 3
                case "End":
                    stare = 0
            
                case _:
                    match stare:
                        case 0:
                            print("ceva dubios s-a întâmplat")
                            return 0 
                        case 1: # literele, trivial
                            dfa["alfabet"].append(l)
                        case 2: # stările, mai mult de facut dar simplu
                            s = l.split(",")
                            #print("TEEEST: ", s)
                            dfa["stari"].append(s[0])
                            for i in range(1, len(s)):
                                match s[i].strip():
                                    case "S":
                                        if dfa["start"] != "":
                                            #print("aici1")
                                            return 0
                                        dfa["start"] = s[0]
                                    case "F":
                                        dfa["final"].append(s[0])
                        case 3: # tranzitii, relativ trivial
                            t = [a.strip() for a in l.split(",")]
                            if t[0] not in dfa["tranzitii"]:
                                dfa["tranzitii"][t[0]] = {}
                            if t[1] not in dfa["tranzitii"][t[0]]:
                                dfa["tranzitii"][t[0]][t[1]] = t[2]

    # ultime verificari
    for i in dfa["tranzitii"]:
        if i not in dfa["stari"]:
            #print("aici2")
            return 0
        for litera in dfa["tranzitii"][i]:
            if litera not in dfa["alfabet"]:
                #print("aici3")
                return 0
    return 1


def acceptare(cuvant, dfa):
    cuvant = cuvant.strip()
    stare = dfa["start"]
    
    for litera in cuvant:
        # print("Am ajuns in starea", stare)
        if litera not in dfa["alfabet"]: # litera nu este in alfabet, deci respingem
            return 0
        if litera not in dfa["tranzitii"][stare]: # litera nu este acoperita de functia de tranzitie, respingem si aici
            return 0
        stare = dfa["tranzitii"][stare][litera]

    if stare in dfa["final"]:
        return 1
    return 0

'''if validare("R1") == 1:
    print("VALID")
else:
    print("INVALID")

cuvant = input().strip()
if acceptare(cuvant) == 1:
    print("Cuvantul {0} este acceptat".format(cuvant))
else:    
    print("Cuvantul {0} este respins".format(cuvant))'''
