import os

class Facture:

	def __init__(self, prestation, non_fichier, lignefichier):
		self._non_fichier = non_fichier
		self._lignefichier = lignefichier
		self._nb_piece = ""
		self._compte_client_trouve = -1 
		self.no_facture = ""
		self._no_piece = ""
		self._prestation = prestation
		self.client = []
		self.nom_client = ""
		self._date = ""
		self.mois = 0
		self.jour = 0
		self.montant_ht = 0.0
		self.montant_tva = 0.0
		self.montant_ttc = 0.0
		self.compte = ""

	def __repr__(self):
		commun = f"Facture : {self.no_facture}, Piece : {self._no_piece}, date : {self._date}, client : {self.client}, ht : {self.montant_ht}, tva : {self.montant_tva}, ttc : {self.montant_ttc}"
		if self._compte_client_trouve == 1 :
			return  "" #f"Compte client OK : {self.compte}, " + commun 
		else :
			return f"Compte client KO : {self.compte}, " + commun 

	def _GenLigne(self, sortie, compte, debit, credit):
		ligne = "1;" + self._date + " 00:00" + ";" + self._no_piece + ";'" + self.no_facture + ";" + compte + ";" + self.nom_client + ";"
		ligne = ligne + f"{debit}".replace(".",",") + ";" + f"{credit}".replace(".",",") + ";" + self._date + " 00:00" + ";;False"  
		sortie.write(ligne + "\n")

	def GenEcriture(self,sortie):
		try :
			for i in range(3):
				if i == 0 :
					self._GenLigne(sortie, self.compte, self.montant_ttc, 0)	
				if i == 1 :
					self._GenLigne(sortie, "4457100", 0, self.montant_tva)	
				if i == 2 :
					self._GenLigne(sortie, self._prestation, 0, self.montant_ht)
		except UnicodeEncodeError :
			print(f"Erreur GenEcriture : {self}")
			exit()

	def _RechercheDep(self):
		ville = ""
		ville = self.client[-1:][0]
		dep = int(ville[0:2])
		return ville[0:2]


	def _AnalyseCompte(self):
		if self.nom_client.find("Pharmacie") != -1:
			nomCompteClient = "PHARMACIES " + self._RechercheDep()
			for client, compte in liste_comptes_client :
					if nomCompteClient == client:
						self.compte = compte
						self._compte_client_trouve = 1
						return
			self.compte = "411PHARMACIE"
			self._compte_client_trouve = 0
			return

		if (self.nom_client.find("Super U") != -1) or (self.nom_client.find("Intermarché") != -1) or (self.nom_client.find("Hyper U") != -1) or (self.nom_client.find("Netto") != -1) or (self.nom_client.find("HAMEL") != -1) or (self.nom_client.find("Vive Le Jardin") != -1) or (self.nom_client.find("U Express") != -1):
			nomCompteClient = "GRANDE SURFACE " + self._RechercheDep()
			for client, compte in liste_comptes_client :
					if nomCompteClient == client:
						self.compte = compte
						self._compte_client_trouve = 1
						return
			self.compte = "411GD"
			self._compte_client_trouve = 0
			return

		for client, compte in liste_comptes_client :
			if (self.nom_client.upper()).find(client) != -1:
				self.compte = compte
				self._compte_client_trouve = 1
				return

		self.compte = "4111"
		self._compte_client_trouve = 0

	def Analyse(self):
		self.nom_client = self.client[0]
		self._AnalyseCompte()

		tva = round(self.montant_ht * 0.2, 2)
		if tva != self.montant_tva:
			print(f" facture {self.nom_client} Problème TVA : TVA relevé = {self.montant_tva} TVA calculée : {tva}")
			print(self)
			print (f"fichier : {self._non_fichier} ligne : {self._lignefichier}")

		ttc = round(self.montant_ht + self.montant_tva, 2)
		if ttc != self.montant_ttc:
			print(f" facture {self.nom_client} Problème TTC : TTC relevé = {self.montant_ttc} TTC calculée : {ttc} = {self.montant_ht} + {self.montant_tva}")
			print(self)
			print (f"fichier : {self._non_fichier} ligne : {self._lignefichier}")

	def setDate(self, date):
		self._date = date
		self.mois = int(date[3:5])
		self.jour = int(date[0:2])

	def setNoPiece(self, numero):
		self._no_piece = "VE" + self._date[8:10] + self._date[3:5] + f"{numero:03d}" 

	def getCompte(self):
		return self._prestation

def Traitementfichier(nomfichier, prestation):
	ligne_nb = 0
	ligne_facture = -1
	ligne_no_facture = -1
	ligne_total_ht = -1
	ligne_tva = -1
	ligne_total_ttc = -1
	nb_piece = 0
	adrresse = 0
	liste_facture = []

	#with open(nomfichier, encoding='latin-1') as entree:
	with open(nomfichier, encoding='latin-1') as entree: 
		for ligne in entree:
			ligne_nb += 1
			longueur_ligne_original = len(ligne)
			ligne = ligne.strip()
			longueur_ligne = len(ligne)

			#print(f"{ligne_nb} : {ligne}")

			if ligne.find("FACTURE") != -1:
				f = Facture(prestation, nomfichier, ligne_nb)
				liste_facture.append(f)
				ligne_facture = ligne_nb
				adresse_trouve = 0

			if ligne_nb == ligne_facture + 1 :
				f.setDate(ligne)

			# Client
			if ligne_nb > ligne_facture + 3 and adresse_trouve < 2 :
				if len(ligne) > 0 :
					adresse_trouve = 1
					f.client.append(ligne)
				if len(ligne) == 0 and adresse_trouve == 1 :
					adresse_trouve = 2
					#print(f.client)

			# No facture
			if ligne.find("N° de facture") != -1:
				ligne_no_facture = ligne_nb

			if (ligne_nb == ligne_no_facture + 2) and (ligne_nb != 1) :
				f.no_facture = ligne.replace("'","")			

			# Montant
			if ligne.find("TOTAL HT") != -1:
				ligne_total_ht = ligne_nb

			if ligne_nb == ligne_total_ht + 1 :
				try :
					f.montant_ht = float(ligne[0:-2].replace(",",".").replace(" ","").replace(u'\xa0',u''))
				except ValueError:
					print(f"Erreur lecture total HT dans fichier {nomfichier}, prestation {prestation} ligne {ligne_nb}")

			if ligne.find("TVA ") != -1:
				ligne_tva = ligne_nb

			if ligne_nb == ligne_tva + 1 :
				try :
					f.montant_tva = float(ligne[0:-2].replace(",",".").replace(" ","").replace(u'\xa0',u''))
				except ValueError:
					print(f"Erreur lecture total TVA dans fichier {nomfichier}, prestation {prestation} ligne {ligne_nb}")

			if ligne.find("TOTAL TTC") != -1:
				ligne_total_ttc = ligne_nb

			if ligne_nb == ligne_total_ttc + 1 :
				try : 
					f.montant_ttc = float(ligne[0:-2].replace(",",".").replace(" ","").replace(u'\xa0',u''))
				except ValueError:
					print(f"Erreur lecture total TTC dans fichier {nomfichier}, prestation {prestation} ligne {ligne_nb}")

	return liste_facture

def TraitementRep(rep,mois, prestation):
	liste_facture_rep = []
	for filename in os.listdir(rep):
		if filename.find(".txt") > 0:
			if mois == str(filename[0:2]):
				liste_facture_rep.extend(Traitementfichier(rep +"/" + filename, prestation))
				print(filename)
	return liste_facture_rep

def ListeFacturesMois(liste_factures, compte, mois):
	liste_factures_jour = []
	for jour in range(1,32):
		for f in liste_factures_clients :
			if (f.getCompte() == compte) and (f.mois == mois) and (f.jour == jour) :
				liste_factures_jour.append(f)
	return liste_factures_jour

def ListeFacturesMoisClasse(liste_factures, mois):
	liste_factures_mois = []
	liste_factures_mois.extend(ListeFacturesMois(liste_factures, "706000", mois))
	liste_factures_mois.extend(ListeFacturesMois(liste_factures, "706005", mois))
	liste_factures_mois.extend(ListeFacturesMois(liste_factures, "706001", mois))
	liste_factures_mois.extend(ListeFacturesMois(liste_factures, "706002", mois))
	liste_factures_mois.extend(ListeFacturesMois(liste_factures, "706004", mois))
	return liste_factures_mois

liste_comptes_client = []
liste_factures_clients = []

with open("LISTE COMPTE CLIENT.csv", "r", encoding='windows-1252') as fichier_comptes_clients :
	for ligne in fichier_comptes_clients:
		champs = ligne.split(";")
		liste_comptes_client.append((champs[1].upper(), champs[0]))
#print(liste_comptes_client)

for i in range(1,13):
	mois = f"{i:02d}"
	print(mois)
	numero_piece_mois = 1
	liste_factures_clients.extend(TraitementRep("ADHESION 706000", mois, "706000"))
	liste_factures_clients.extend(TraitementRep("COMMISSION 706005", mois, "706005"))
	liste_factures_clients.extend(TraitementRep("FOURNISSEUR 706001", mois, "706001"))
	liste_factures_clients.extend(TraitementRep("PRESTATION 706002", mois, "706002"))
	liste_factures_clients.extend(TraitementRep("SUIVI 706004", mois, "706004"))

for f in liste_factures_clients :
	f.Analyse()

#Numerotation des pièces
for mois in range(1,13):
	numero = 1 
	for facture in ListeFacturesMoisClasse(liste_factures_clients, mois) :
		facture.setNoPiece(numero)
		numero += 1

#with open("analyse.txt", "w", encoding='windows-1252') as fichier_analyse :
with open("analyse KO.txt", "w", encoding='latin-1') as fichier_analyse :
	for f in liste_factures_clients :
		if str(f) != "" :
			fichier_analyse.write(str(f) + "\n")

for mois in range(1,13):
	non_fichier = "ecritures" + f"{mois:02d}" + ".csv"
	#with open(non_fichier, "w", encoding='windows-1252') as ecritures:
	with open(non_fichier, "w", encoding='latin-1') as ecritures:
		ligne = "Statut;Jour;Pièce;Document;Compte général;Libellé;Débit;Crédit;Date de l'échéance;Poste analytique;Documents associés"
		ecritures.write(ligne + "\n")
		for facture in ListeFacturesMoisClasse(liste_factures_clients, mois) :
			facture.GenEcriture(ecritures)
