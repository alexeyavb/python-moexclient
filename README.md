# python-moexclient
Moscow Exchange client

```
$ moex security find пик
+--------------+--------------+------------+--------------------------------+--------------+-----------------+
| secid        | isin         | shortname  | name                           | group        | primary_boardid |
+--------------+--------------+------------+--------------------------------+--------------+-----------------+
| RU000A0JXQ93 | RU000A0JXQ93 | ПИК БО-П02 | ГК ПИК (ПАО) БО-П02            | stock_bonds  | TQCB            |
| RU000A0JXK40 | RU000A0JXK40 | ПИК БО-П01 | ГК ПИК (ПАО) БО-П01            | stock_bonds  | TQCB            |
| RU000A100XR0 | RU000A100XR0 | ПИК К 1P1  | ПИК-Корпорация 001Р-01         | stock_bonds  | TQCB            |
| RU000A0ZZBJ7 | RU000A0ZZBJ7 | ПИК БО-П07 | ГК ПИК ПАО БО-П07              | stock_bonds  | TQCB            |
| RU000A0ZZ1M2 | RU000A0ZZ1M2 | ПИК БО-П04 | ГК ПИК ПАО БО-П04              | stock_bonds  | TQCB            |
| RU000A0JXY44 | RU000A0JXY44 | ПИК БО-П03 | ГК ПИК (ПАО) БО-П03            | stock_bonds  | TQCB            |
| RU000A0ZZAW2 | RU000A0ZZAW2 | ПИК БО-П06 | ГК ПИК ПАО БО-П06              | stock_bonds  | TQCB            |
| RU000A0JWP46 | RU000A0JWP46 | ПИК БО-7   | ГК ПИК (ПАО) БО-07             | stock_bonds  | TQCB            |
| PIKK         | RU000A0JP7J7 | ПИК ао     | Группа компания ПИК ПАО ао     | stock_shares | TQBR            |
| RU000A1016Z3 | RU000A1016Z3 | ПИК К 1P2  | ПИК-Корпорация 001Р-02         | stock_bonds  | TQCB            |
| RU000A1026C1 | RU000A1026C1 | ПИК К 1P3  | ПИК-Корпорация 001Р-03         | stock_bonds  | TQCB            |
| PIK-ME       | US69338N2062 | PIK-гдр    | ГДР ГруппаКомпаний ПИК ORD SHS | stock_dr     | RPMO            |
+--------------+--------------+------------+--------------------------------+--------------+-----------------+
$ moex security show PIKK
+----------------------+----------------------------+
| Field                | Value                      |
+----------------------+----------------------------+
| EMITTER_ID           | 1323                       |
| EVENINGSESSION       | 1                          |
| FACEUNIT             | SUR                        |
| FACEVALUE            | 62.5                       |
| GROUP                | stock_shares               |
| GROUPNAME            | Акции                      |
| ISIN                 | RU000A0JP7J7               |
| ISQUALIFIEDINVESTORS | 0                          |
| ISSUEDATE            | 2007-06-13                 |
| ISSUESIZE            | 660497344                  |
| LATNAME              | PIK                        |
| LISTLEVEL            | 1                          |
| NAME                 | Группа компания ПИК ПАО ао |
| REGNUMBER            | 1-02-01556-A               |
| SECID                | PIKK                       |
| SHORTNAME            | ПИК ао                     |
| TYPE                 | common_share               |
| TYPENAME             | Акция обыкновенная         |
+----------------------+----------------------------+
$
```
