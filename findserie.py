#! python3
# fndseries.p - Script qui doit trouver/idenifie les sous-titres puis identife la bonne version
#puis placer et ben renomme le fichier telecharge
import logging, requests, bs4, webbrowser, zipfile, re
logging.basicConfig(level=logging.INFO, format=' %(asctime)s -%(levelname)s - %(message)s')
def findserie(serieTitre, serieSaison, serieEpisode, serieSource, serieTeam, fullpathEpisode):
    serie_titre_formatted = serieTitre.lower().replace(' ', '+')

    logging.info("Searching for %s .." % (serieTitre)) # display text while downloading the search page
    res = requests.get('https://www.sous-titres.eu/search.html?q=' + serie_titre_formatted)
    res.raise_for_status()



    # Retrieve top search result links.
    soup = bs4.BeautifulSoup(res.text)
    # Open a browser tab for each result.
    linkElems = soup.select('.icone')

    for i in range(1):
        serie_page = 'http://www.sous-titres.eu/' + linkElems[i].get('href')


    logging.info("Searching for Saison %s Episode %s .." % (serieSaison, serieEpisode)) # display
    res = requests.get(serie_page)
    res.raise_for_status()



    # Retrieve top search result links.
    soup = bs4.BeautifulSoup(res.text)
    href_formatted = "a[href*="+serieSaison+"x"+serieEpisode+"]"
    # Open a browser tab for each result.
    linkElems = soup.select(href_formatted)
    for i in range(1):
        #webbrowser.open('http://www.sous-titres.eu/series/' + linkElems[i].get('href'))
        res = requests.get('http://www.sous-titres.eu/series/' + linkElems[i].get('href'))
        res.raise_for_status()
        zipTempFile = open('zipTemp.zip', 'wb')
        for chunk in res.iter_content(100000):
            zipTempFile.write(chunk)
        zipTempFile.close()
        logging.info("Fichier ZIP cree")
        zipTempFile2 = zipfile.ZipFile('zipTemp.zip')
        liste_fichier = zipTempFile2.namelist()
        logging.info("Choix du bon fichier soustitres")
        choix_st_Pattern1 = re.compile(r"""^((.*)%s
            (.*)(VF|FR)(.*)\.ass$
            )

            """ % serieTeam, re.VERBOSE|re.IGNORECASE)
        choix_st_Pattern2 = re.compile(r"""^((.*)%s
            (.*)(VF|FR)(.*)\.srt$
            )

            """ % serieTeam, re.VERBOSE|re.IGNORECASE)
        choix_st_Pattern3 = re.compile(r"""^((.*)%s
            (.*)(VF|FR)(.*)\.ass$
            )

            """ % serieSource, re.VERBOSE|re.IGNORECASE)
        choix_st_Pattern4 = re.compile(r"""^((.*)%s
            (.*)(VF|FR)(.*)\.srt$
            )

            """ % serieSource, re.VERBOSE|re.IGNORECASE)
        liste_choix = []
        for fichier in liste_fichier:
            mo = choix_st_Pattern1.search(fichier)
            mo2 = choix_st_Pattern2.search(fichier)
            mo3 = choix_st_Pattern3.search(fichier)
            mo4 = choix_st_Pattern4.search(fichier)
                # Skip si mauvais formatting
            if mo == None and mo2 == None and mo3 == None and mo4 == None:
                continue
            elif mo!=None:
                bon_fichier1 = mo.group(0)
                liste_choix[0] = bon_fichier1
            elif mo2!=None:
                bon_fichier2 = mo2.group(0)
                liste_choix.append(bon_fichier2)
            elif mo3!=None:
                bon_fichier3 = mo3.group(0)
                liste_choix.append(bon_fichier3)
            elif mo4!=None:
                bon_fichier4 = mo4.group(0)
                liste_choix.append(bon_fichier4)
        if liste_choix != []:
            logging.info("Fichier sous titres trouve .. "+liste_choix[0])
            zipTempFile2.extract(liste_choix[0], fullpathEpisode+'.fr.ass')
        else:
            logging.info("Pas de bon fichier trouve")

findserie("The Expanse", '1', '06', 'HDTV', 'viethd', 'L:\\Grabbed\\alt.binaries.teevee\\The Expanse\\The Expanse - 01 x 06 - Rock Bottom')
