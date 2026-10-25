# Vi du DRL voi Drools (Java + Maven)

Repository nay minh hoa cach dung **DRL (Drools Rule Language)** de tach logic nghiep vu khoi ma Java. Vi du tinh chiet khau don hang theo hang khach hang.

## Yeu cau

- JDK 17 tro len
- Maven 3.9 tro len
- Ket noi Internet o lan build dau tien de tai dependency Maven

## Chay vi du

```bash
mvn clean test
mvn -q exec:java -Dexec.mainClass=com.example.drl.App
```

Lenh `exec:java` duoc cau hinh bang Maven Exec Plugin trong `pom.xml`. Ban cung co the chay `com.example.drl.App` tu IDE sau khi import project Maven.

## Quy tac mau

File `src/main/resources/rules/discount.drl` co cac quy tac:

- Khach hang `GOLD`: giam 15% neu don hang tu 100 tro len.
- Khach hang `SILVER`: giam 10% neu don hang tu 200 tro len.
- Cac truong hop khac: khong giam gia.

## Cau truc thu muc

```text
src/main/java/com/example/drl/
  App.java                     # Chay demo tu terminal/IDE
  model/Order.java              # Du lieu don hang (fact)
  service/DiscountService.java  # Nap va chay rule engine
src/main/resources/
  META-INF/kmodule.xml          # Cau hinh KIE session
  rules/discount.drl            # Quy tac DRL
src/test/java/                  # JUnit 5 tests
docs/DRL_GUIDE_VI.md             # Huong dan DRL bang tieng Viet
.github/workflows/maven.yml     # Tu dong chay test tren GitHub Actions
```

## Chay test

```bash
mvn clean verify
```

GitHub Actions cung chay lenh nay khi co push len `main` hoac khi mo pull request vao `main`.

## Tim hieu them

Doc [`docs/DRL_GUIDE_VI.md`](docs/DRL_GUIDE_VI.md) de xem cu phap `rule`, `when`, `then`, `modify`, cach them rule va loi thuong gap.

## Academic research toolkit

Xem [huong dan research hoc thuat bang tieng Viet](research-workflow/README_VI.md) de chay cong cu Python tim metadata qua OpenAlex va Crossref, khử trùng lặp, xuat CSV/BibTeX/JSON va tao nhat ky tim kiem. Workflow tu dong nam tai `.github/workflows/academic-research.yml`; chon Actions -> Academic literature search -> Run workflow de bat dau.
