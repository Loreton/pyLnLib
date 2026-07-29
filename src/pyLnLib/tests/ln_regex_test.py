#!/usr/bin/env python3
#
# Progamma per testare regex
# ruff: noqa: SIM210 - Remove unnecessary `True if ... else False` help: Remove unnecessary `True if ... else False` (Ruff SIM210)


import sys
sys.dont_write_bytecode = True

import json
from pathlib import Path








from pyLnLib.logger import init_logger
# from pyLnLib.regex import multi_near_words
from pyLnLib import regex
from pyLnLib.colors import get_colors
C = get_colors()


# ----------------------------
# ----- logging
# ----------------------------

def function_executing_time(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        logger.notify(f"[Function: {func.__name__}] eseguita in {end - start:.6f} secondi", stacklevel=1)
        return result
    return wrapper








def get_data() -> str:
    content: str = """
        \n \n \n \n \n \n \n \n \n \n \n \n \n 2434 \n \n
        \n Questo romanzo è un’opera di fantasia. Tutti i nomi, i personaggi, i luoghi \n e gli avvenimenti descritti sono frutto dell’immaginazione dell’autrice o sono usati \n in maniera fittizia. Qualunque analogia con società, \n fatti, luoghi o persone reali, esistenti o esistite, è puramente casuale e non voluta dall’autrice. \n \n Titolo originale:   ’ Til Death \n Copyright © 2014 Bella Jewel \n All rights reserved \n \n Traduzione dalla lingua inglese di Francesca Noto \n Prima edizione ebook: novembre 2019 \n © 2019 Newton Compton editori s.r.l., Roma \n \n ISBN 978-88-227-3856-1 \n \n www.newtoncompton.com \n \n Edizione elettronica realizzata da Manuela Carrara per   Corpotre, Roma \n \n
        \n \n \n Bella Jewel \n Amami fino alla fine \n \n \n \n \n Newton Compton editori \n \n
    \n    Indice\r\n   \n \n Copertina \n \n \n Logo \n \n \n Colophon \n \n \n Frontespizio \n \n \n Dedica \n \n \n \n \n \n Prologo \n \n \n Capitolo 1 \n \n \n Capitolo 2 \n \n \n Capitolo 3 \n \n \n Capitolo 4 \n \n \n Capitolo 5 \n \n \n Capitolo 6 \n \n \n Capitolo 7 \n \n \n Capitolo 8 \n \n \n Capitolo 9 \n \n \n Capitolo 10 \n \n \n Capitolo 11 \n \n \n Capitolo 12 \n \n \n Capitolo 13 \n \n \n Capitolo 14 \n \n \n Capitolo 15 \n \n \n Capitolo 16 \n \n \n Capitolo 17 \n \n \n Capitolo 18 \n \n \n Capitolo 19 \n \n \n Capitolo 20 \n \n \n Capitolo 21 \n \n \n Capitolo 22 \n \n \n Capitolo 23 \n \n \n Capitolo 24 \n \n \n Capitolo 25 \n \n \n Capitolo 26 \n \n \n Capitolo 27 \n \n \n Capitolo 28 \n \n \n Capitolo 29 \n \n \n Capitolo 30 \n \n \n \n \n \n Ringraziamenti \n \n
        \n Questo libro è dedicato a tutte le belle il cui cuore è stato distrutto da una bestia. \n \n \n \n \n \n \n Nota \n Vi prego di ricordare che questa è un’opera di fantasia, e io, come autrice, non credo in alcun modo che  possa accadere  nella vita reale. Niente di quello che leggete è ispirato a fatti realmente accaduti. \n \n \n
        Prologo \n Katia \n Lasciate che vi racconti una storia. È una di quelle storie che vi scatenerà dentro un odio tale da bruciarvi l’anima. Potrebbe perfino farvi odiare me. In fondo, io ho sposato  lui . \n Lui sarebbe Marcus. \n L’uomo che è entrato nella mia vita come un uragano e ha sconvolto il mio mondo, rovesciandolo. L’uomo che amo così tanto da sapere che mi segnerà in modo irreversibile. È un uomo che distrugge la vita di chi incontra, ma la rende al tempo stesso bellissima. Il mio Marcus cambierà anche il vostro mondo, se glielo permetterete. \n E glielo permetterete, perché è così che funziona, con lui. \n Lo amo in modo profondo e sbagliato. Lo so perché, per quanto il mio cuore mi gridi che è sbagliato, non riesco a stare lontana da lui. Marcus è duro, cupo, per niente dolce e gentile, ma quando è dentro di me, io lo sento. Sento tutto quello che si rifiuta di farmi vedere. Ed è incredibile. Ed è così che si è insinuato in me e ci è rimasto. \n Quella che è iniziata come la storia di una notte si è presto trasformata in tutta la mia esistenza. Non saprei dirvi come sia successo, e neanche perché, ho solo capito che non riuscivo più a fare a meno di lui. Non aveva importanza quello che faceva. Prima che potessi davvero razionalizzare quella scelta, l’avevo sposato. Una settimana dopo, sono andata a vivere da lui. Tutte le persone intorno a me erano felici. Tranne forse Marcus. Lui era rimasto il solito, impassibile e intenso, così profondo da non farmi entrare. \n Dicono che il corpo riesce ad avvertirti, quando qualcosa diventa pericoloso, che inizia a vibrare per la consapevolezza. E hanno ragione. Io l’ho sentito; ho avvertito il cambiamento, e ho capito, nel momento in cui sono entrata nel mondo di Marcus, che lui mi avrebbe strappato via l’anima e con tutta probabilità l’avrebbe distrutta. Mi sono innamorata di un uomo di cui quasi nessuna donna si innamorerebbe, perché  puzza  di cuori spezzati e sofferenze lontano un miglio. Non è il tipo da cuori e fiori, non ti abbraccia con affetto, non ti chiama con nomignoli dolci, né ti fa sentire  come se fossi  l’unico motivo per cui respira. \n Nell’accettarlo, sono diventata la ragazza di cui parlano tutti,  sapete quale . Quella che ti fa scuotere la testa, domandandoti perché resti al fianco di quell’uomo, e perché sia lì, tanto per cominciare. Come può essere così stupida? Cosa può mai vedere in uno stronzo come quello? Ecco, quella sono io. Anche se all’inizio non me ne sono resa conto. Mi sono innamorata del diavolo. Non lo sapevo,  a quel  tempo, e anche se l’avessi saputo, non posso dire con certezza che avrei fatto scelte diverse. Mi ci è voluto tempo per capire chi fosse davvero Marcus; per capire che il mio amore non era ricambiato. \n Ma era questo, capite? Amore. Profondo e sconvolgente, un amore di cui non riuscivo a liberarmi. \n Mi ha consumato. Ha preso il mio cuore nelle sue mani e continua a possederlo. \n Non riesco in alcun modo a stare lontana da lui. \n La Katia che sono adesso scomparirà in un mondo di sofferenze e bugie. Non esisterà più. Lui mi prenderà e farà a pezzi il mio mondo finché  smetterà di essere  bello  e diventerà  orribile. Così orribile da seppellirmi. So bene che forse non uscirò da questa storia illesa. \n Ma sto andando troppo avanti. Devo cominciare dall’inizio. \n \n \n \n \n
        Capitolo 1 \n Allora \n Marcus \n Le mie dita tamburellano contro la scrivania di legno scuro di pino, mentre osservo l’avvocato dalla calvizie incipiente e dall’aria acida  che legge  il testamento di mio nonno. Un testamento che mi hanno chiamato ad ascoltare. Il vecchio bastardo mi odiava, ma a quanto pare ha deciso comunque di includermi nel suo prezioso testamento, che sta mandando al manicomio la famiglia. Tutti ne vogliono un pezzo. \n «Signor Tandem, grazie per essere venuto, oggi». \n Niente nella mia espressione cambia, mentre l’avvocato parla in tono basso e professionale. Alza gli occhi  per  guardarmi, quando non rispondo, imbronciando le labbra e osservandomi da capo a piedi. \n «Possiamo procedere?», domando, spostandomi sulla sedia. «Ho da fare». \n Lui si schiarisce la gola. «Certamente. Immagino che abbia già capito perché si trova qui, oggi». \n «A dire il vero», rispondo con freddezza, incrociando le braccia sul petto. «Non ne ho idea». \n «Ebbene, come di sicuro sa, suo nonno è di recente venuto a mancare.  Da quello che ho inteso, lei lo ha aiutato a gestire gli affari, negli ultimi dieci anni». \n «L’ho fatto da solo», puntualizzo. «Quel vecchio bastardo non ha fatto altro che starsene con le mani in mano e far lavorare gli altri al suo posto. E ora è morto e l’unica cosa che interessa a tutti quanti è ottenere un pezzo di quello che potrebbe essersi lasciato alle spalle». \n «In ogni caso, ha lasciato precise istruzioni per la sua impresa,  in caso di decesso. Ed è per questo che l’ho fatta chiamare qui». \n «Si sbrighi», scatto, stringendo gli occhi e fissandolo con astio. \n «Molto bene. Suo nonno ha stabilito che la sua impresa passasse a lei.  Lei è l’unico suo discendente diretto, dal decesso di suo padre, perciò l’unico a cui lui abbia voluto lasciare la sua impresa». \n Be’, il vecchio è servito a qualcosa, almeno. Non che non me l’aspettassi, del resto: sono coinvolto nei suoi affari da tanto tempo. I miei fratellastri non sono mai stati niente, per lui, quindi resto soltanto io. \n «D’accordo. Del resto, sto già gestendo i suoi affari, quindi non vedo cosa dovrebbe cambiare». \n «C’è qualcos’altro», risponde l’avvocato, allentandosi la cravatta come se fosse di colpo troppo stretta. «Ha stabilito con molta chiarezza che c’è una condizione da rispettare, perché  lei possa essere a capo della sua impresa. Se vuole diventarlo, deve essere...». \n «Cosa?», sbotto. \n «Sposato, signore». \n Prego? \n Lo guardo fisso, aspettando che scoppi a ridere e mi dica che era solo uno scherzo, ma la sua espressione resta impassibile. \n «Mi sta prendendo per i fondelli», sbuffo. «Deve aver capito male». \n «Nel testamento viene chiaramente espresso che, finché lei non sarà sposato, l’impresa resterà in mano al suo più caro amico, Walter Johnson. Lei manterrà la sua posizione, ma non potrà  ereditare le finanze e la gestione della compagnia». \n Fottuto Walter, quello stronzo calcolatore. Manderà tutto a puttane prima che io possa fare qualsiasi cosa. È già il presidente e mi fa sgobbare come un disperato, e di sicuro si aggrapperà al suo posto come una piattola, se non faccio qualcosa. In fondo, ora sta nuotando nell’oro. Io sono l’unico che tiene davvero alla compagnia.  L’unico, cazzo . È la mia vita e la mia salvezza; lo è stata da quando avevo vent’anni, e il mio attuale stile di vita si basa su questo lavoro. \n In tono basso e roco, mormoro: «È proprio sicuro che dica che debba sposarmi?» \n «Sì, signore, ne sono sicuro. Ha dodici mesi di tempo per farlo, prima che la compagnia   passi  a Walter». \n Cazzo. \n Io adoro le donne. Tutte le donne. Ma non mi piace che mi stiano intorno. Se vogliono una storia seria, non devono guardare me.  Nono sono mai andato a letto con la stessa donna per più di una volta, fatta una sola eccezione, ed è stato esclusivamente per convenienza . L’amore non fa per uomini come me. Non ho né il tempo, né l’interesse per pensarci. L’amore è per i deboli. Le donne sono troppo difficili e io sono troppo stronzo. Non lo nascondo e non fingo altrimenti. Ho visto dov’è che le relazioni crollano, e non voglio finire in situazioni simili. \n «C i sono altre disgrazie che deve comunicarmi?», domando, a denti stretti. \n Gli occhi dell’avvocato hanno un guizzo, poi deglutisce. «Ci sono delle condizioni. Non può sposarsi per divorziare subito dopo. Deve restare sposato per almeno due anni. Se dovesse divorziare prima, la compagnia andrebbe a Walter». \n Ma stiamo scherzando? \n Che malato figlio di puttana. \n Lo sapeva... sapeva  benissimo  che questa era l’unica cosa che poteva mettermi in difficoltà. Era un uomo crudele e deviato da vivo, e a quanto pare ha continuato a esserlo anche da morto. Mi sta mettendo alla prova, mi sta spingendo al limite, come ha sempre fatto. E così, dovrò decidere se mollare, perdendo tutto quello per cui ho lavorato negli ultimi dieci anni, oppure lottare per ottenere ciò che è sempre stato mio. Questa compagnia è la mia vita, e quel maledetto bastardo lo sapeva. \n «C’è altro?», ringhio, digrignando i denti. \n «Un’ultima cosa, signore. Se si dovesse scoprire che lei... ah...», deglutisce, «...ha pagato per avere una moglie, anche questo basterebbe a far andare la compagnia a Walter. La donna in questione deve sposarla di sua spontanea volontà e vivere con lei  dopo il matrimonio». \n Che pezzo di merda . Mi conosceva meglio di quanto pensassi. Sapeva che il mio primo pensiero sarebbe stato quello di cercare una stupida da pagare per sposarmi. Stringo i denti e sento il petto riempirsi di rabbia. Riesco già a immaginare la faccia di Walter se la compagnia venisse consegnata a lui. Mi ha sempre odiato. No, non gli permetterò di vincere. \n Maledetto vecchio. Erano anni che voleva che mi accasassi,  ha sempre odiato  il mio stile di vita da celibe. Spesso mi diceva che anche se non volevo, per gestire una compagnia e avere un nome rispettato nella società avrei dovuto fare buon viso a cattivo gioco e sposarmi. Lui si era sposato a vent’anni con una stronza che è morta un paio d’anni fa. E anche dopo la sua dipartita, lui ha continuato a fingere di aver avuto un matrimonio perfetto. Non mi sorprende che sia arrivato a questo per assicurarsi che mi incastrassi anch’io con una donna. \n «Molto bene», affermo, alzandomi in piedi. «Vedrò di sbrigarmi a risolvere questa faccenda». \n L’avvocato mi rivolge un’occhiata carica di disgusto. «E come pensa di fare?». \n Gli sorrido, sornione. «Semplice. Troverò una moglie». \n \n \n \n \n
        Capitolo 2 \n Allora \n Katia \n Click, click, click . \n I miei tacchi sono solo uno dei rumori che risuonano sulla strada affollata, mentre mi affretto a raggiungere il luogo del compleanno del mio migliore amico, Dusty. C’è un brusio di voci, intorno a me, mentre la gente si dirige verso le varie destinazioni del sabato sera. Non  riesco  a evitare di sorridere alle persone che incrocio, felice di essere lontana dal lavoro e nel mondo del relax. \n Sono l’assistente personale di un capo dispotico che gestisce una grossa compagnia di spedizioni. Passo giorni lavorativi frenetici, e l’unico momento che ho per ricaricarmi è il weekend. E anche in quel caso, la pace non è garantita. Prendiamo oggi, per esempio: il capo mi ha chiamato per aiutarlo con una presentazione, mentre in realtà sarei voluta solo rimanere a letto. \n «Ehi, ragazza!». \n Sorrido, avvicinandomi al locale in cui ho appuntamento con Dusty. È già lì davanti, tutto vestito di nero, elegante e bellissimo. Mi sorride, correndo ad abbracciarmi. Rido, lasciando che mi sollevi e mi faccia girare in cerchio. \n «Buon compleanno, Dust», ridacchio, quando mi posa di nuovo a terra. \n «Amica mia, stai benissimo!». \n Dusty è il gay più simpatico, amichevole e sexy che abbia mai avuto il piacere di conoscere. Siamo diventati amici poco meno di cinque anni fa, e siamo rimasti molto uniti da allora. L’ho incontrato in un bar, mentre piangeva nel suo drink, per così dire, dopo essere stato lasciato. Abbiamo iniziato a chiacchierare, ci siamo sbronzati e l’amicizia è iniziata. Mi ha chiamato il giorno dopo, e ora eccoci qui. \n «Ho dovuto lavorare tutto il giorno», mi lamento. \n Lui arriccia il naso e agita una mano, disgustato. Rido, mentre i suoi occhi blu scintillano di divertimento. Ha una carnagione tra il chiaro e l’olivastro, è alto, muscoloso ed eccezionale. \n «Ragazza mia, tu lavori troppo. Vuoi che dica due parole al tuo capo?». Ammicca. \n Sogghigno e gli stringo le braccia intorno al corpo, premendo una guancia contro il suo petto. «Nah». \n Lui mi abbraccia stretta. «Secondo me ti stai stressando, con tutto questo lavoro», mi sussurra all’orecchio, facendosi più serio. \n «Ma devo farlo. Mia madre ha bisogno di quei soldi e...». \n «Lo so, tesoro, ma non meriti neanche tutta questa tensione». \n Mi scosto, sorridendogli. «Sto bene». \n «Lavori sessanta ore a settimana, come minimo». \n Agito una mano, alzando gli occhi al cielo alla sua piccola esagerazione. «Ora sono qui, no?». \n Lui mi lancia uno sguardo scettico e torna a sorridere. «Dimmi», riprende, prendendomi a braccetto e conducendomi verso il bar, «dove diavolo hai trovato quelle scarpe meravigliose?». \n \n «Katia, lo giuro, sei più carina ogni volta che ti vedo!». \n Sono avvolta nell’abbraccio di Candy, la mia migliore amica, anche se  non riusciamo a vederci   più di tanto  perché vive a due ore di macchina da me. È allegra, spumeggiante e dolce. La sua personalità è come una droga, non ne puoi più fare a meno. Ed è anche molto intelligente. Lavora per una grossa compagnia che, da quel che ho capito, affitta enormi macchinari. \n «Potrei dire lo stesso», esclamo, al di sopra della musica, scostandomi dall’abbraccio. \n Lei mi sorride, mostrandomi una fila di denti candidi e perfetti. Su uno di loro c’è perfino una specie di piccolo diamante. Non so come si chiamano quei gioielli, ma mi piacciono. \n Candy è bellissima, pur restando una ragazza normale. Ha i capelli castani, gli occhi nocciola, una pelle perfetta e uno splendido corpo. Non è una bionda da urlo e neanche una bellezza esotica, ma è così carina e adorabile che passerei le giornate a strizzarle le guance. \n Lei sbuffa. «Noi due siamo come il cane e la sua cacca». \n Scoppio a ridere. «Cosa?» \n «Tu sei il cane, tutto carino e delizioso, e io sono la cacca. Da solo, il cane non si crede un granché, ma in realtà fa sentire tutti gli altri come se fossero la sua cacca». \n La fisso, sbattendo le palpebre. «Stai scherzando?». \n Lei ridacchia. «No! Te lo giuro, fai sembrare tutti gli altri in quel modo». \n Alzo gli occhi al cielo. \n «Non fare quel gesto con me, e... ohhh, dove le hai comprate quelle scarpe?». \n Sorrido e la prendo a braccetto, raccontandole tutto delle scarpe e della fortuna che ho avuto nel trovarle del colore giusto. \n «Ah!», sospira. «Lo stile di vita di chi è ricco e famoso». \n Sbuffo. «Ho dovuto mettere i soldi da parte per cinque mesi e le ho trovate in un negozio di seconda mano! E comunque, hai un lavoro bellissimo. A proposito, come sta andando?». \n Lei sorride, portandosi una ciocca di capelli dietro un orecchio. «Lo adoro, davvero. Insomma, d’accordo,  è passata solo una settimana, ma finora mi è piaciuto moltissimo. E il capo... oh, mio Dio, dovresti vederlo, Kat. È pazzesco». \n «Ehi, condividi un po’? Ho bisogno di un  po’ di materiale per la mia banca delle fantasie erotiche». \n Lei mi guarda con aria sgomenta. «E cosa ci fa una ragazza come te e con il tuo aspetto  con  una banca delle fantasie erotiche?» \n «Non ho tempo per un  fidanzato». \n «Ma potresti comunque trovarti qualcuno da portarti a letto...», puntualizza lei. \n Scuoto la testa, indietreggiando. Candy adora mettere insieme la gente. No, per davvero. Pensa di essere brava a creare le coppie perfette. Ma non è vero. L’ultimo ragazzo che mi ha presentato ha scorreggiato durante la cena.  Giuro . Poi si è messo a ridere come se non avesse davvero fatto una cosa del genere in un lussuoso ristorante italiano. È stato un momento fantastico. No, davvero, non c’è niente di sbagliato in una rumorosa scorreggia dentro a un ristorante, vero? \n «Non ci provare!». \n Lei imbroncia le labbra, adorabile come sempre. «Okay, magari no, ma potremmo trovarti un bel pezzo di manzo da portarti a casa e ripassarti come si deve». \n Ripassarmi ? Ma chi parla più così, al giorno d’oggi? \n «Non mi   ripasserò  proprio nessuno», protesto. \n Ma non sarebbe una cattiva idea, in realtà. Jack e Teddy, i miei vibratori, avrebbero bisogno di una vacanza. E Dio, mi manca davvero la compagnia maschile. Sono passati due anni dall’ultima volta in cui ho avuto un appuntamento romantico, e almeno uno dall’ultima volta che ho fatto sesso. Ucciderei qualcuno per fare del buon sesso, anche solo contro un muro, o piegata sul cofano di una macchina, e per dare sfogo a tutte queste fantasie sessuali che mi crescono dentro. \n Di certo, al lavoro non ho niente su cui fantasticare. Il mio capo è obeso, puzzolente e stronzo. Perché non posso avere un capo super sexy che sembra saltato giù dal paradiso? Uno che mi porta a fare giri in elicottero e mi lega al suo letto? \n Perché? Perché questo è il mondo reale, gente. Nessun capo è mai così pazzesco. Accidenti a te, Christian Grey, per  avermi  rovinato tutti i capi che potrò mai conoscere. Non potranno mai vincere contro di te. \n «Ehiiii!», esclama Candy, facendomi schioccare le dita davanti alla faccia. \n Sbatto le palpebre. Merda. «Scusa, stavo fantasticando a occhi aperti su Christian Grey». \n Lei mi fissa, mortificata. «Lo sai che non è una persona reale, vero?» \n «Rimangiatelo subito», sibilo. «Per me lui è reale, e anche per Jack e Teddy». \n «Neanche i tuoi vibratori sono persone reali, tesoro». \n Sussulto. «E ti metti anche a insultarli. Come osi?». \n Lei scoppia a ridere. «Dobbiamo procurarti del buon sesso. Subito». \n Temo che abbia ragione. \n «D’accordo, ma a certe condizioni», affermo, sorseggiando il mio drink. «Non deve puzzare, non deve fare scorregge, non deve essere calvo e... non devono mancargli dei denti». \n Lei apre la bocca per parlare, ma la interrompo. \n «E neanche  altre parti del corpo!», esclamo. «Deve avere tutte le dita, delle mani e dei piedi... capito?». \n Lei mi fissa in silenzio. «Santo cielo, hai davvero bisogno di sesso». \n Probabilmente è vero. \n «Avanti», mi incalza. «Andiamo in bagno, ti mettiamo in tiro e poi ti siedi al bancone come la stronzetta sexy che sei e   rimedi  il tuo pezzo di manzo per stanotte». \n Andiamo in bagno e ci facciamo strada a spinte in mezzo alle ragazze ubriache che lo affollano per arrivare a uno specchio. Osservo il mio riflesso, sorpresa di essere riuscita a tirare fuori un look così bello con il poco tempo che avevo a disposizione. Ho recuperato dall’armadio il mio vestito rosso più sexy, che lascia la schiena scoperta, con uno scollo profondo sul davanti, corto e stretto. E poi ho cercato tra le mie tante scarpe per trovarne un paio adatte, nere e con i tacchi a spillo. Non ci ho messo tanto a sistemarmi i capelli: sono biondi e lunghi fino alla vita, e li avevo arricciati questa mattina, lasciandoli sciolti al lavoro. \n Neanche il trucco è stato difficile, sebbene abbia gli occhi un po’ arrossati. Verdi e profondi, oggi sembrano piuttosto spenti e stanchi. Ecco cosa succede quando passi tutto il tuo tempo davanti allo schermo di un computer. Prendo il mascara dalla borsetta e lo applico, poi concludo il tutto con il rossetto scarlatto. La mia pelle non ha bisogno di molto make-up: mio padre era italiano e ho ereditato la sua perfetta pelle olivastra. Ho visto una sola foto dello stallone che era da giovane, ma di certo era un bell’uomo. \n Mia madre è una donna stupenda, e non mi sorprende che, a un certo punto della sua vita, abbia avuto tante attenzioni maschili. Anche lei è bionda, solo che ha la carnagione molto chiara, e gli occhi verdi come i miei. È una donna minuta, ed è da lei che ho ereditato la corporatura. Non ho le gambe molto lunghe, ecco perché adoro le scarpe con i tacchi chilometrici. Mi chiamano da sempre folletto. \n Ci sono volte in cui considero che mi sarebbe piaciuto conoscere mio padre, ma mia madre non mi ha mai voluto raccontare molto di lui. Non conosco la loro storia. Non so cosa sia successo tra loro. Non so neanche se sappia di me. Conosco solo il suo nome.  Pierre . Tutto qui. \n Mia madre non parla più tanto, ormai, non dopo il tumore al cervello. Gliel’hanno diagnosticato cinque anni fa ed è stato operato quasi subito. Nel corso dell’intervento, alcuni nervi essenziali sono stati danneggiati e lei è rimasta paralizzata. Non ha il controllo delle gambe ed è costretta su una sedia a rotelle, ma almeno ha il controllo del resto del corpo, dopo una lunga riabilitazione, e riesce a parlare, sebbene con la voce un po’ tremula. Mi sono presa cura di lei, da allora; sono l’unica parente che ha, e non posso permettermi di farle avere un’assistenza a tempo pieno. \n Posso soltanto permettermi una persona che si occupa di lei quando sono al lavoro. \n È difficile e stressante, ma non smetterei mai di farlo. Mai. \n «Dio, come fanno i tuoi capelli a essere così lucenti e con quei boccoli così sexy?», mi domanda Candy, passandomi le dita tra le ciocche e tirandole dispettosa. \n «Con tanta fatica», ribatto io, scostandole le mani e cominciando a occuparmi dei suoi, di capelli. Ha una splendida chioma liscia. Non so proprio perché si lamenti. \n «Accidenti ai tuoi meravigliosi capelli italiani, che i l cielo li maledica!». \n Rido piano e le batto una pacca sulle spalle. «Ecco qui, sei bellissima». \n Lei si controlla, poi guarda me, e infine annuncia: «È ora di trovarti un uomo». \n Riceviamo qualche sguardo astioso, mentre passiamo in mezzo alle altre ragazze che si stanno sistemando. Candy borbotta qualcosa del tipo “scattate una foto” e usciamo in fretta dal bagno. Procediamo lungo i corridoi del locale, con me davanti, e proprio mentre svolto l’angolo per tornare nella sala principale, sbatto contro un corpo alto e muscoloso. Con uno sbuffo esplosivo, barcollo sui tacchi, e due mani mi afferrano per le braccia, evitandomi di cadere. \n Mi raddrizzo e faccio un passo indietro. Non riesco a vedere altro che una camicia bianca, immacolata e semplice, con una cravatta rosso scuro. La camicia è tesa su un petto davvero muscoloso. Alzo con lentezza gli occhi e sussulto nel ritrovarmi a fissare uno dei volti più attraenti che abbia mai visto, ancora più bello di quello di Dusty... al diavolo, perfino migliore di Brad Pitt o di Christian Grey. Okay, forse di Christian Grey, no, starei un po’ esagerando... scuoto la testa e mi perdo negli occhi più scuri che abbia mai incrociato. \n Sono praticamente neri. \n La mascella, abbassata verso di me perché anche lui mi sta fissando da capo a piedi, è coperta di un velo ispido di barba che gli dona un aspetto professionale ma anche pericoloso. Ha folti capelli neri che si arricciano appena alla base del collo. La mandibola è forte e solida, le labbra piene e sensuali. E non fatemi neanche cominciare a dire qualcosa sulla sua altezza o su quei muscoli che noto quando muove un braccio. La camicia bianca ha le maniche arrotolate fino ai gomiti e wow, quei muscoli incordati risalgono fino al punto in cui scompaiono sotto al tessuto. Da far venire l’acquolina in bocca. \n Riesco a notare un tatuaggio che gli spunta da sotto ai capelli, girandogli intorno al collo, e noto un’ombra anche sotto la camicia, a intendere che quel tatuaggio continua anche oltre. Oh, cielo. Lo osservo mentre i suoi occhi mi fissano da capo a piedi, proprio come ho fatto io con lui. E li vedo lampeggiare di apprezzamento, sebbene non sorrida; le sue labbra restano tirate in una linea netta e dura. \n «Mi scusi», mormoro, con la voce affannata. \n Non riesce neanche a sentirmi, la musica è troppo alta. \n «Marcus?». \n Questa è Candy, che mi arriva alle spalle. \n Conosce questo dio del sesso? \n «Candice», risponde Marcus e, mio Dio, la sua voce è come miele fuso...   e sabbiosa allo stesso tempo , però, perché il miele da solo non basta a descriverla. «Cosa ci fai qui?» \n «Io, ah...», balbetta lei. \n «È con me», spiego, alzando lo sguardo nei suoi occhi. «Per una festa di compleanno». \n «La tua?», mormora, fissando le mie labbra. \n Gesù. \n «No», deglutisco. «Di un nostro amico». \n Lui riporta lo sguardo su Candy. «Hai lasciato le chiavi in ufficio. Le ho date a Jemimah». \n Quindi, questo è il suo capo? Il capo sexy di cui mi parlava? \n Dannazione. Devo andare a lavorare da lei. \n «Mi spiace,  signore ». \n Signore? \n Oh, cielo. \n «E tu chi sei?». \n Mi ci vuole un minuto per capire che ha riportato l’attenzione su di me. \n «Katia», rispondo, leccandomi le labbra. \n Lui porta gli occhi proprio in quel punto e li vedo riempirsi di desiderio. Oh, cielo. Lui! Scelgo lui! Potrebbe finalmente interrompere il periodo di siccità... merda, credo ci sia già riuscito, a giudicare dallo stato dei miei slip. Mi sdraierei davanti a un autobus, per avere un assaggio di lui. Oh, sì, sì, altroché se lo farei. \n «Katia», lo sento ronfare. «Posso offrirti da bere?». \n Candy squittisce, accanto a me. Porto lo sguardo su di lei e vedo che ha gli occhi sgranati. Mi piego verso di lei, prendendola a braccetto. «Dimmi che posso portarmi a letto il tuo capo senza problemi, ti prego». \n Le ci vuole un attimo per rispondere, e quando lo fa, la sua voce è un pigolio sommesso: «Io, ah, io non...». \n «Dio, ti prego, dimmi che posso. Ho bisogno di un po’ di Marcus». \n «È un donnaiolo», mi sussurra. \n «Non gli sto mica chiedendo di sposarmi», sbuffo. «Solo un po’ di sano su e giù...». \n «Katia», mi chiama Marcus, interrompendomi. \n Mi giro verso di lui, offrendogli uno sguardo innocente. «Sì, puoi offrirmi da bere». \n Candy bisbiglia un’imprecazione rivolta a nessuno in particolare e Marcus mi passa un braccio intorno alla vita, conducendomi al bancone del locale. Superiamo Dusty, nel farlo, e lui sgrana gli occhi, per poi sogghignare sornione e rivolgermi i pollici in alto e qualche movimento pelvico che Marcus riesce a notare. Vedo le sue labbra arricciarsi, e, Dio santo, questo lo rende ancora più sexy. \n Marcus ordina i drink senza chiedermi di cosa io abbia voglia. Mi pare ovvio che sia uno a cui piace controllare ogni cosa. Quando i bicchieri arrivano, mi conduce in un giardino interno più tranquillo, dove ci sediamo. Dannazione, la tensione sessuale tra noi è potentissima. Mi giro verso di lui, accavallando le gambe e lasciando che mi guardi ancora. Si capisce ciò che vuole, non ne sta facendo un segreto; è tutto nei suoi occhi. E io non me ne sento affatto offesa; mi prenderò tutto quello che vorrà darmi. Può anche legarmi e sculacciarmi, se gli va. \n «Katia»,  mormora, in quel suo modo sensuale. «Dimmi, cosa fai nella vita?» \n «Lavoro come assistente personale in una grossa compagnia di consegne». \n Mi studia, mentre parlo, come se mi stesse considerando lui stesso per un lavoro. \n «Sei sveglia». \n Non è una domanda, ma fingo lo sia. \n E sbuffo. «Non arriverei a dirlo. Faccio bene il mio lavoro, ma fino a dire di essere sveglia...». \n Lui mi osserva con attenzione, come se stesse cercando di studiarmi. \n «Dimmi qualcos’altro di te». \n Okay. Strano. \n Gli racconto un po’ di me, senza andare troppo nei dettagli, e ancora una volta mi pare quasi di essere a un colloquio di lavoro. Lui mi ascolta con attenzione, nel frattempo, e quando gli racconto di mia madre e dei miei sforzi per tenerla a casa, qualcosa cambia, nei suoi occhi. Non saprei dire con esattezza cosa, ma c’è un cambiamento. \n «Mi sembri molto occupata». \n «Non ho molte opportunità di rilassarmi, questo è certo.  Se smettessi di lavorare, mia madre non avrebbe il supporto di cui ha bisogno». \n Lui annuisce, studiandomi. «Un altro drink?». \n Annuisco. \n Tutto questo è strano. Sexy... ma strano. \n Agita una mano verso un cameriere che si ferma e viene da noi. Marcus ordina un altro drink, senza mai staccare lo sguardo da me. \n «Sei una bellissima ragazza, Katia», mormora. «Quindi, lo dirò fuori dai denti. Ti va di venire a casa mia, stasera?». \n Eccolo. \n Bam . \n Sento il corpo scaldarsi e le gambe tremare. Se voglio andare a casa di Marcus? Diavolo, posso essere piuttosto sicura che non è un serial killer, visto che Candy lavora per lui. Non sto cercando una relazione stabile e lui è spettacolare. Quindi, la risposta è semplice. \n Uhm,  cazzo, sì ! \n «Sì», rispondo, leccandomi il labbro  inferiore. \n Lui segue la mia lingua con gli occhi. «Cazzo», mormora. \n Ecco, questo posto è appena diventato parecchio più caldo. \n Lo vedo allungare un braccio e con il dorso delle dita mi accarezza la mascella. Basta quel movimento a fermare del tutto il mio mondo. La pelle formicola e i sensi si svegliano di colpo. Le s
        Capitolo 3 \n borsa \n Katia \n strillo Click, borsa strillo
        parlano proprio tutti perché
        """

    return content


##############################################################
# - Parse Input
##############################################################
import argparse
def ParseInput() -> argparse.Namespace:
    from types import SimpleNamespace
    l=SimpleNamespace()
    l.default_color = C.yellow
    l.default = f'{l.default_color}(default: %(default)s){C.reset}\n\n'
    l.metavar_optional=f'{C.white}<optional>{C.reset}'
    l.metavar_mandatory=f'{C.white}<mandatory>{C.reset}'

    def searchingFlags(my_parser):
        flags = my_parser.add_argument_group(f'{C.white}Searching flags{C.reset}')
        flags.add_argument('--boundary',  action='store_true', default=False, required=False,
                help=f'{C.cyan}full words instead of partial strings {l.default}')

        flags.add_argument('--ignore-case',  action='store_true', default=False, required=False,
                help=f'{C.cyan}case insensitive {l.default}')

        flags.add_argument('--context-length',  type=int, default=0, metavar='', required=False,
                help=f'{C.cyan}text-len of extra Text before and after the searched string {l.default}')

        # wd_required = True if '--near' in sys.argv else False
        flags.add_argument('--words-distance',  type=int, nargs=2, metavar='', default=[1, 5], required=False,
                help=f'{C.cyan}(MIN MAX) distance between words {l.default_color}(dafault no-limits){C.reset}')


    def operatorsFlags(my_parser):
        operation = my_parser.add_argument_group(f'{C.white}Operators Group (mandatory) {C.reset}')
        operators_group = operation.add_mutually_exclusive_group(required=True)
        operators_group.add_argument('--and-search',    action='store_true', default=False, help=f'{C.cyan}and between words{C.reset}')
        operators_group.add_argument('--and-any-order',    action='store_true', default=False, help=f'{C.cyan}and between words in any order{C.reset}')
        operators_group.add_argument('--or',     action='store_true', default=False, help=f'{C.cyan}or several words{C.reset}')
        operators_group.add_argument('--near',   action='store_true', default=False, help=f'{C.cyan}match string{C.reset}')
        operators_group.add_argument('--near-any-order',   action='store_true', default=False, help=f'{C.cyan}match word in any order{C.reset}')
        operators_group.add_argument('--string', action='store_true', default=False, help=f'{C.cyan}match string{C.reset}')

    # wd_required = True if '--near' in sys.argv else False
    # flags.add_argument('--words-dist',  type=int, nargs=2, metavar='', default=[], required=wd_required,
    #         help=f'{C.cyan}(MIN MAX) distance between words {C.reset}(dafault no-limits)')
    # -----------------------------
    if len(sys.argv) == 1:
        sys.argv.append('-h')


    parser = argparse.ArgumentParser(description='ebooks test')
    operatorsFlags(parser)
    searchingFlags(parser)
    parser.add_argument('--display-args',    action='store_true', default=False, help=f'{C.cyan}display results{C.reset}')
    args = parser.parse_args()

    if args.display_args:
        import json
        json_data = json.dumps(vars(args), indent=4, sort_keys=True)
        print(json_data)
        # print(f'input arguments: {json_data}'.format(**locals()))
        sys.exit(0)


    return  args


####################################################
#
####################################################
def chack_near_words(data: str):
    words_list=["chiama", "nomignoli"]
    words_list=["chiama", "nomignoli", "sentire"]
    words_list=["saprei", "successo", "neanche",  "capito",  "riuscivo", "importanza"]
    words_distance: list = [1, 30]
    occurrencies = regex.multi_near_words( source_data=data,
                                    words_list=words_list,
                                    words_distance=words_distance,
                                    normalize_text=False,
                                    ignore_case=True,
                                    context_length=100 )
    logger.debug(occurrencies)
    if len(occurrencies) > 0:
        logger.info("words to find: \n%s", words_list)
        for item in occurrencies:
            content = item.context
            for word in words_list:
                content=content.replace(word, f"{C.yellowH}{word}{C.reset}")
            logger.info(content)
    else:
        logger.info("non trovate")


####################################################
#
####################################################
def chack_near_words_any_order(data: str):
    # mischiamo le words_list, dovrebberossere trovate tutte
    words_list=[ "importanza", "saprei", "SUCCESSO", "capito",  "riuscivo","neanche"]
    words_distance: list = [1, 30]
    occurrencies = regex.multi_near_words_any_order( source_data=data,
                                    words_list=words_list,
                                    words_distance=words_distance,
                                    normalize_text=False,
                                    ignore_case=True,
                                    context_length=100 )
    logger.debug(occurrencies)
    if len(occurrencies) > 0:
        logger.info("words to find: \n%s", words_list)
        for item in occurrencies:
            content = item.context
            for word in words_list:
                content=content.replace(word, f"{C.yellowH}{word}{C.reset}")
            logger.info(content)
    else:
        logger.info("non trovate")


####################################################
#
####################################################
def chack_AND_search(data: str):
    words_list=["saprei", "successo", "neanche",  "capito",  "riuscivo", "importanza"]
    words_distance: list = [1, 30]
    # words_distance: list = [0,0]
    occurrencies = regex.and_search( source_data=data,
                                    words_list=words_list,
                                    words_distance=words_distance,
                                    normalize_text=False,
                                    ignore_case=True,
                                    any_order=True,
                                    context_length=100 )
    logger.debug(occurrencies)
    if len(occurrencies) > 0:
        logger.info("words to find: \n%s", words_list)
        for item in occurrencies:
            content = item.context
            for word in words_list:
                content=content.replace(word, f"{C.yellowH}{word}{C.reset}")
            logger.info(content)
    else:
        logger.info("non trovate")


####################################################
#
####################################################
def chack_AND_any_order(data: str):
    # mischiamo le words_list, dovrebberossere trovate tutte
    words_list=[ "importanza", "saprei", "SUCCESSO", "capito",  "riuscivo","neanche"]
    words_distance: list = [0,0]
    words_distance: list = [1, 30]
    occurrencies = regex.and_search( source_data=data,
                                    words_list=words_list,
                                    words_distance=words_distance,
                                    normalize_text=False,
                                    any_order=True,
                                    ignore_case=True,
                                    context_length=100 )
    logger.debug(occurrencies)
    if len(occurrencies) > 0:
        logger.info("words to find: \n%s", words_list)
        for item in occurrencies:
            content = item.context
            for word in words_list:
                content=content.replace(word, f"{C.yellowH}{word}{C.reset}")
            logger.info(content)
    else:
        logger.info("non trovate")



if __name__ == '__main__':
    logger = init_logger()
    args = ParseInput()
    data: str = get_data()
    mydata = ' '.join(data.split()) ### --- normalize source data

    if args.near:
        chack_near_words(data)
    elif args.near_any_order:
        chack_near_words_any_order(data)
    elif args.and_search:
        chack_AND_search(data)
    elif args.and_any_order:
        chack_AND_any_order(data)

    sys.exit("Temporary exit")


    if args.STRING:
        result: list = lnRE.STRING(   source_data=mydata,
                            stringa=args.STRING,
                            word_boundary=args.boundary,
                            normalize_text=False,
                            context_length=args.context_length,
                            ignore_case=args.ignore_case)

        for index, item in enumerate(result):
            json_data=json.dumps(item, indent=True, sort_keys=False, separators=(',', ': '), default=str)
            print(f"[{index:02}]:", json_data)



    elif args.OR:
        result = lnRE.OR(   source_data=mydata,
                            string_list=args.OR,
                            word_boundary=args.boundary,
                            context_length=args.context_length,
                            normalize_text=False,
                            return_dict=True,
                            ignore_case=args.ignore_case)

        notFounds=0
        # print(result)
        # import pdb; pdb.set_trace() # by Loreto
        for key, value in result.items():
            logger.info("%-10s: %s", key, value)
            if value == "NOT_FOUND":
                notFounds += 1

        n_occurrencies = len(result)
        if n_occurrencies > 0:
            logger.notify("OK - %s string/s was/were found", n_occurrencies)
        else:
            logger.error("ERRORE - NO string found.")
        if notFounds > 0:
            logger.warning("[%s NOT FOUND] NOT ALL the strings were found", notFounds)





    elif args.AND:
        result = lnRE.AND_justCheck(source_data=mydata,
                                    string_list=args.AND,
                                    word_boundary=args.boundary,
                                    normalize_text=False,
                                    ignore_case=args.ignore_case)
        if not result:
            logger.error("ERRORE - some string not found.")



        ### --- return DICT
        result = lnRE.AND(  source_data=mydata,
                            string_list=args.AND,
                            word_boundary=args.boundary,
                            context_length=args.context_length,
                            normalize_text=False,
                            ignore_case=args.ignore_case,
                            return_dict=True,
                            exit_on_first_notfound=False)

        notFounds=0
        for key, value in result.items():
            logger.info("%-10s: %s", key, value)
            if value == "NOT_FOUND":
                notFounds += 1

        n_occurrencies = len(result)
        if n_occurrencies > 0:
            logger.notify("OK - %s string/s was/were found", n_occurrencies)
        else:
            logger.error("ERRORE - NO string found.")
        if notFounds > 0:
            logger.warning("[%s NOT FOUND] NOT ALL the strings were found", notFounds)

        from keybPrompt import keyb_prompt; keyb_prompt() # by Loreto

        ### --- return LIST
        result = lnRE.AND(  source_data=mydata,
                            string_list=args.AND,
                            word_boundary=args.boundary,
                            context_length=args.context_length,
                            normalize_text=False,
                            ignore_case=args.ignore_case,
                            return_dict=False,
                            exit_on_first_notfound=False)

        notFounds=0
        for key, value in result.items():
            logger.info("%-10s: %s", key, value)
            if value == "NOT_FOUND":
                notFounds += 1

        n_occurrencies = len(result)
        if n_occurrencies > 0:
            logger.notify("OK - %s string/s was/were found", n_occurrencies)
        else:
            logger.error("ERRORE - NO string found.")
        if notFounds > 0:
            logger.warning("[%s NOT FOUND] NOT ALL the strings were found", notFounds)






        # Caso 1: Parentesi tonde
    elif args.tonda:
        test_data = "Questo è un esempio (  di stringa1 ) e qui (  di stringa2 ) e qui c'è un altro ${valore_importante} in un testo."

        prefix = "("
        suffix = ")"
        risultato1 = lnRE.FindEnclosedStrings(test_data, prefix, suffix)
        print(test_data)
        print(f"Prefisso='{prefix}', Suffisso='{suffix}' -> Risultato: {risultato1}")

        new_data = lnRE.FindFirstEnclosed(test_data, prefix, suffix, replace_with="")
        print(test_data)
        print(new_data)

        result = lnRE.FindFirstEnclosed(test_data, prefix, suffix, replace_with=None)
        print(test_data)
        json_data=json.dumps(result, indent=True, sort_keys=False, separators=(',', ': '), default=str)
        print(json_data)


        # Caso 2: Graffe e dollaro (caratteri speciali che richiedono re.escape)
    elif args.variable:
        test_data = "Questo è un esempio ( di stringa ) e qui c'è un altro ${valore_importante} in un testo."
        prefix = "${"
        suffix = "}"
        prefix = "esempio"
        suffix = ""
        risultato1 = lnRE.FindEnclosedStrings(test_data, prefix, suffix)
        print(test_data)
        print(f"Prefisso='{prefix}', Suffisso='{suffix}' -> Risultato: {risultato1}")

        new_data = lnRE.FindFirstEnclosed(test_data, prefix, suffix, replace_with="")
        print(test_data)
        print(new_data)

        result = lnRE.FindFirstEnclosed(test_data, prefix, suffix, replace_with=None)
        print(test_data)
        json_data=json.dumps(result, indent=True, sort_keys=False, separators=(',', ': '), default=str)
        print(json_data)
        # Output: ['valore_importante']

        # Caso 3: Nessuna corrispondenza
    elif args.minor:
        test_data = "Questo è un esempio (di stringa) e qui c'è un altro ${valore_importante} in un testo."
        prefix3 = "<"
        suffix3 = ">"
        risultato3 = lnRE.FindEnclosedStrings(test_data, prefix3, suffix3)
        print(f"Prefisso='{prefix3}', Suffisso='{suffix3}' -> Risultato: {risultato3}")
        # Output: []




    print()
