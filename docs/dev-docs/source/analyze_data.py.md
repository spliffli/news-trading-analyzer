# analyze_data.py

## Overview

- [ ] **TODO:** Update this section

## Functions:

### `get_decimal_places`

**Description**
This function takes a float number as an input argument and returns the number of decimal places in that number.

**Signature**
```python
def get_decimal_places(num: float) -> int:
```

**Parameters**

- **`num` (`float`)**: The input number for which the decimal places need to be determined.

**Returns**

- `int`: The number of decimal places in the input float number `num`.

**Example Usage**

```python
>>> get_decimal_places(123.456)
3
```

**Notes**

- The function converts the input number to a string, splits it at the decimal point, and retrieves the second part of the resulting list (which represents the digits after the decimal point).
- It calculates the length of the decimal digits string to determine how many decimal places the original number has.
- The function assumes that the input is a proper float with a decimal point; it does not handle edge cases where the input might be an integer or a string.

