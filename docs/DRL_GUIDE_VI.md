# Huong dan DRL (Drools Rule Language)

## 1. DRL la gi?

DRL la ngon ngu khai bao quy tac cua Drools. Thay vi viet toan bo dieu kien nghiep vu trong cac nhanh `if/else` cua Java, ta mo ta dieu kien va hanh dong thanh cac rule doc lap. Rule engine se so khop cac fact (doi tuong du lieu) voi phan dieu kien va thuc thi cac rule phu hop.

DRL huu ich khi quy tac nghiep vu thay doi thuong xuyen, can duoc doc rieng, kiem thu rieng hoac quan ly boi nhom nghiep vu va ky thuat.

## 2. Cau truc mot rule

```drl
package rules
import com.example.drl.model.Order

rule "Gold customer discount"
    when
        $order : Order(customerTier == "GOLD", total >= 100, discountApplied == false)
    then
        modify($order) {
            setDiscountRate(0.15),
            setDiscountApplied(true)
        }
end
```

- `package`: ten package logic cua rule, khong nhat thiet trung voi package Java.
- `import`: khai bao class Java duoc su dung trong rule.
- `rule "..." `: bat dau mot quy tac co ten.
- `when`: phan dieu kien (left-hand side). Trong vi du, don hang phai la hang GOLD, co tong tien tu 100 tro len va chua ap dung giam gia.
- `$order`: bien lien ket toi object `Order` khop dieu kien.
- `then`: phan hanh dong (right-hand side) se chay khi rule duoc kich hoat.
- `modify`: cap nhat object va thong bao cho rule engine rang fact da thay doi.
- `end`: ket thuc rule.

## 3. Vi du trong repository

File `src/main/resources/rules/discount.drl` co hai rule:

| Hang khach | Dieu kien | Muc giam |
| --- | --- | --- |
| GOLD | Tong don >= 100 | 15% |
| SILVER | Tong don >= 200 | 10% |
| Khac | Khong khop hai rule tren | 0% |

`Order` la fact. `DiscountService` tao `KieSession`, insert fact, goi `fireAllRules()` de chay cac rule khop, sau do dispose session trong khoi `finally`.

## 4. Chay code va test

Can JDK 17+ va Maven 3.9+.

```bash
mvn clean test
mvn clean verify
```

De xem ket qua mau, chay class `com.example.drl.App` trong IDE sau khi import project Maven, hoac dung:

```bash
mvn -q exec:java -Dexec.mainClass=com.example.drl.App
```

Vi du output:

```text
GOLD | total=200.00 | discount=15% (30.00) | final=170.00
SILVER | total=250.00 | discount=10% (25.00) | final=225.00
REGULAR | total=300.00 | discount=0% (0.00) | final=300.00
GOLD | total=50.00 | discount=0% (0.00) | final=50.00
```

JUnit tests kiem tra ca khop rule va truong hop khong du dieu kien. GitHub Actions chay `mvn --batch-mode --no-transfer-progress clean verify` khi push hoac pull request vao `main`.

## 5. Cach them rule moi

1. Xac dinh du lieu can dung va dam bao Java fact co getter/setter tuong ung.
2. Them rule vao `src/main/resources/rules/discount.drl`.
3. Viet dieu kien ro rang trong `when`; tranh dieu kien qua rong co the kich hoat nhieu lan.
4. Trong `then`, cap nhat fact bang `modify` neu thay doi cua object can duoc rule engine nhan biet.
5. Viet JUnit test cho ca duoc ap dung va khong duoc ap dung.
6. Chay `mvn clean verify` truoc khi push.

## 6. Loi thuong gap

- **Rule khong duoc chay:** kiem tra package DRL, duong dan resource, `kmodule.xml`, ten KIE session va dieu kien trong `when`.
- **Rule lap vo han:** kiem tra viec `update`/`modify` co lam dieu kien tiep tuc dung hay khong. Trong vi du nay, `discountApplied` duoc dat thanh `true` de ngan rule ap dung lai.
- **Sai ten property:** DRL su dung JavaBean getter; vi du `customerTier` duoc doc tu `getCustomerTier()` va `discountApplied` tu `isDiscountApplied()`.
- **Sai ket qua tien te:** can lam tron o ranh gioi nghiep vu. Vi du dung `double` de don gian; ung dung tai chinh thuc te nen can nhac `BigDecimal`.

## 7. Goi y khi dua vao production

- Giu rule don gian, dat ten co y nghia va viet test cho ranh gioi.
- Tranh goi dich vu ben ngoai co side effect truc tiep trong `then`.
- Quan ly version cua rule va theo doi thay doi nghiep vu.
- Dung `BigDecimal` cho tinh toan tien te can do chinh xac thap phan.
- Xem xet quy tac xung dot va salience chi khi that su can thiet; khong nen dung do uu tien de che giau dieu kien chong cheo.
