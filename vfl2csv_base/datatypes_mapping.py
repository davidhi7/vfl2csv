import pandas as pd

pandas_datatypes_mapping = {
    "string": pd.StringDtype(),
    "int8": pd.Int8Dtype(),
    "int16": pd.Int16Dtype(),
    "int32": pd.Int32Dtype(),
    "int64": pd.Int64Dtype(),
    "uint8": pd.UInt8Dtype(),
    "uint16": pd.UInt16Dtype(),
    "uint32": pd.UInt32Dtype(),
    "uint64": pd.UInt64Dtype(),
    "float32": pd.Float32Dtype(),
    "float64": pd.Float64Dtype(),
}
