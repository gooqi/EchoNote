#[derive(Debug, thiserror::Error)]
pub enum Error {
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),
    #[error("ZIP file not found")]
    ZipFileNotFound,
    #[error("ZIP extraction error: {0}")]
    ZipExtract(#[from] zip::result::ZipError),
    #[error("File error: {0}")]
    File(#[from] echonote_file::Error),
}

#[derive(
    Debug,
    Eq,
    Hash,
    PartialEq,
    Clone,
    strum::EnumString,
    strum::Display,
    serde::Serialize,
    serde::Deserialize,
    specta::Type,
)]
pub enum VoskModel {
    #[serde(rename = "SmallCn")]
    SmallCn,
    #[serde(rename = "LargeCn")]
    LargeCn,
    #[serde(rename = "SmallEn")]
    SmallEn,
    #[serde(rename = "LargeEn")]
    LargeEn,
}

impl VoskModel {
    pub fn file_name(&self) -> &str {
        match self {
            VoskModel::SmallCn => "vosk-model-small-cn-0.22",
            VoskModel::LargeCn => "vosk-model-cn-0.22",
            VoskModel::SmallEn => "vosk-model-small-en-us-0.15",
            VoskModel::LargeEn => "vosk-model-en-us-0.22",
        }
    }

    pub fn display_name(&self) -> &str {
        match self {
            VoskModel::SmallCn => "Vosk Small (Chinese)",
            VoskModel::LargeCn => "Vosk Large (Chinese)",
            VoskModel::SmallEn => "Vosk Small (English)",
            VoskModel::LargeEn => "Vosk Large (English)",
        }
    }

    pub fn model_url(&self) -> &str {
        match self {
            VoskModel::SmallCn => {
                "https://alphacephei.com/vosk/models/vosk-model-small-cn-0.22.zip"
            }
            VoskModel::LargeCn => "https://alphacephei.com/vosk/models/vosk-model-cn-0.22.zip",
            VoskModel::SmallEn => {
                "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
            }
            VoskModel::LargeEn => "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip",
        }
    }

    pub fn model_size_bytes(&self) -> u64 {
        match self {
            VoskModel::SmallCn => 42_000_000,
            VoskModel::LargeCn => 1_300_000_000,
            VoskModel::SmallEn => 40_000_000,
            VoskModel::LargeEn => 1_800_000_000,
        }
    }

    pub fn is_multilingual(&self) -> bool {
        false
    }

    pub fn supported_language(&self) -> &str {
        match self {
            VoskModel::SmallCn | VoskModel::LargeCn => "zh",
            VoskModel::SmallEn | VoskModel::LargeEn => "en",
        }
    }

    pub fn is_downloaded(&self, base_dir: impl AsRef<std::path::Path>) -> Result<bool, Error> {
        let model_path = base_dir.as_ref().join(self.file_name());

        if !model_path.exists() {
            return Ok(false);
        }

        if !model_path.is_dir() {
            return Ok(false);
        }

        let entries = std::fs::read_dir(&model_path)?;
        let has_files = entries.count() > 0;

        Ok(has_files)
    }

    pub fn zip_verify_and_unpack(
        &self,
        input_path: impl AsRef<std::path::Path>,
        output_path: impl AsRef<std::path::Path>,
    ) -> Result<(), Error> {
        if !input_path.as_ref().exists() {
            return Err(Error::ZipFileNotFound);
        }

        extract_zip_file(&input_path, &output_path)?;
        let _ = std::fs::remove_file(&input_path);
        Ok(())
    }

    pub async fn download<F: Fn(echonote_download_interface::DownloadProgress) + Send + Sync>(
        &self,
        output_path: impl AsRef<std::path::Path>,
        progress_callback: F,
    ) -> Result<(), Error> {
        echonote_file::download_file_parallel(self.model_url(), output_path, progress_callback)
            .await?;
        Ok(())
    }
}

fn extract_zip_file(
    zip_path: impl AsRef<std::path::Path>,
    extract_to: impl AsRef<std::path::Path>,
) -> Result<(), Error> {
    let file = std::fs::File::open(zip_path.as_ref())?;
    let mut archive = zip::ZipArchive::new(file)?;
    std::fs::create_dir_all(extract_to.as_ref())?;

    for i in 0..archive.len() {
        let mut file = archive.by_index(i)?;
        let outpath = match file.enclosed_name() {
            Some(path) => extract_to.as_ref().join(path),
            None => continue,
        };

        if file.is_dir() {
            std::fs::create_dir_all(&outpath)?;
        } else {
            if let Some(p) = outpath.parent() {
                if !p.exists() {
                    std::fs::create_dir_all(p)?;
                }
            }
            let mut outfile = std::fs::File::create(&outpath)?;
            std::io::copy(&mut file, &mut outfile)?;
        }
    }

    Ok(())
}
