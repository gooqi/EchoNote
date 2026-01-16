#[macro_export]
macro_rules! common_event_derives {
    ($item:item) => {
        #[derive(serde::Serialize, Clone, specta::Type, tauri_specta::Event)]
        $item
    };
}

common_event_derives! {
    #[serde(tag = "type")]
    pub enum DetectEvent {
        #[serde(rename = "micStarted")]
        MicStarted {
            key: String,
            apps: Vec<echonote_detect::InstalledApp>,
        },
        #[serde(rename = "micStopped")]
        MicStopped {
            apps: Vec<echonote_detect::InstalledApp>,
        },
        #[serde(rename = "micMuted")]
        MicMuteStateChanged { value: bool },
    }
}

impl From<echonote_detect::DetectEvent> for DetectEvent {
    fn from(event: echonote_detect::DetectEvent) -> Self {
        match event {
            echonote_detect::DetectEvent::MicStarted(apps) => Self::MicStarted {
                key: uuid::Uuid::new_v4().to_string(),
                apps,
            },
            echonote_detect::DetectEvent::MicStopped(apps) => Self::MicStopped { apps },
            #[cfg(all(target_os = "macos", feature = "zoom"))]
            echonote_detect::DetectEvent::ZoomMuteStateChanged { value } => {
                Self::MicMuteStateChanged { value }
            }
        }
    }
}
