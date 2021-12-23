#### Envelop ProtocolV1 Rules
15   14   13   12   11   10   9   8   7   6   5   4   3   2   1   0  <= Bit number in rules(dec)
------------------------------------------------------------------------------------  
 1    1    1    1    1    1   1   1   1   1   1   1   1   1   1   1
 |    |    |    |    |    |   |   |   |   |   |   |   |   |   |   |
 |    |    |    |    |    |   |   |   |   |   |   |   |   |   |   +-No_Unwrap
 |    |    |    |    |    |   |   |   |   |   |   |   |   |   +-No_Wrap 
 |    |    |    |    |    |   |   |   |   |   |   |   |   +-No_Transfer
 |    |    |    |    |    |   |   |   |   |   |   |   +-No_Collateral
 |    |    |    |    |    |   |   |   |   |   |   +-reserved_core
 |    |    |    |    |    |   |   |   |   |   +-reserved_core
 |    |    |    |    |    |   |   |   |   +-reserved_core  
 |    |    |    |    |    |   |   |   +-reserved_core
 |    |    |    |    |    |   |   |
 |    |    |    |    |    |   |   |
 +----+----+----+----+----+---+---+
     for use in extendings