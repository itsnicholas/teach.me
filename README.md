# teach.me opetussovellus

### Tietokannat ja web-ohjelmointi

## Kuvaus

Sovelluksen avulla voidaan järjestää verkkokursseja, joissa on tekstimateriaalia ja automaattisesti tarkastettavia tehtäviä. Jokainen käyttäjä on opettaja tai opiskelija.

## Sovelluksen ominaisuuksia

* Käyttäjä voi kirjautua sisään ja ulos sekä luoda uuden tunnuksen.
* Opiskelija näkee listan kursseista ja voi liittyä kurssille.
* Opiskelija voi lukea kurssin tekstimateriaalia sekä ratkoa kurssin tehtäviä.
* Opiskelija pystyy näkemään tilaston, mitkä kurssin tehtävät hän on ratkonut.
* Opettaja pystyy luomaan uuden kurssin, muuttamaan olemassa olevaa kurssia ja poistamaan kurssin.
* Opettaja pystyy lisäämään kurssille tekstimateriaalia ja tehtäviä. Tehtävä voi olla ainakin monivalinta tai tekstikenttä, johon tulee kirjoittaa oikea vastaus.
* Opettaja pystyy näkemään kurssistaan tilaston, keitä opiskelijoita on kurssilla ja mitkä kurssin tehtävät kukin on ratkonut.

## Sovelluksen käyttöohje

1. Asenna postgres
  
2. Kloonaa tämä repositorio
```
git clone https://github.com/itsnicholas/teach.me.git
```
3. Siirry repositorioon
```
cd teach.me
```
4. Luo postgresiin tietokanta
```
psql -d teachme < schema.sql
```
5. Luo projektin juurihakemistoon .env-tiedosto
```
DATABASE_URI=postgresql:///teachme
SECRET_KEY=<salainen-avain>
```
6. Aktivoi virtuaaliympäristö
```
python3 -m venv venv
source venv/bin/activate
```
7. Asenna sovelluksen riippuvuudet
```
pip install -r requirements.txt
```
8. Käynnistä sovellus
```
flask run
```
