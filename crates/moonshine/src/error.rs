#[derive(Debug, thiserror::Error)]
pub enum Error {
    #[error(transparent)]
    Io(#[from] std::io::Error),

    #[error(transparent)]
    HyprOnnx(#[from] echonote_onnx::Error),

    #[error(transparent)]
    Ort(#[from] echonote_onnx::ort::Error),

    #[error("invalid model name: {0}")]
    InvalidModelName(String),

    #[error("shape error: {0}")]
    Shape(String),

    #[error("tokenizer load error: {0}")]
    TokenizerLoad(String),

    #[error("other: {0}")]
    Other(String),
}
