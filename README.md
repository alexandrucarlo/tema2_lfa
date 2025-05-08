# Tema 2 - Limbaje formale și automate
Programul este structurat în două fișiere:
  - main.py (aici se află explicitarea operației de concatenare, convertorul în postfix, convertirea în NFA prin alg. lui Thompson, și convertirea în DFA prin construcția de subseturi)
  - acceptor.py (luată din tema 1, are funcțiile pt. validarea DFA-urilor și acceptarea cuvintelor)

Pentru buna înțelegere a cititorului, codul este comentat în ambele fișiere.

Pentru fiecare expresie regulată, programul va genera un config file precum cel din tema 1, îl va valida, iar după va parsa fiecare cuvânt și va declara dacă cuvântul are starea de acceptare precum cea specificată în json.
