use futures_util::StreamExt;

use echonote_gbnf::Grammar;
use echonote_llm_interface::ModelManager;
use echonote_template_app_legacy::{Template, render};

pub async fn generate_title(
    provider: &ModelManager,
    ctx: serde_json::Map<String, serde_json::Value>,
) -> Result<String, crate::Error> {
    let model = provider.get_model().await?;

    let stream = model.generate_stream(echonote_llama::LlamaRequest {
        messages: vec![
            echonote_llama::LlamaMessage {
                role: "system".into(),
                content: render(Template::TitleSystem, &ctx).unwrap(),
            },
            echonote_llama::LlamaMessage {
                role: "user".into(),
                content: render(Template::TitleUser, &ctx).unwrap(),
            },
        ],
        max_tokens: Some(30),
        grammar: Some(Grammar::Title.build()),
        ..Default::default()
    })?;

    let items = stream
        .collect::<Vec<_>>()
        .await
        .into_iter()
        .filter_map(|r| match r {
            echonote_llama::Response::TextDelta(content) => Some(content.clone()),
            _ => None,
        })
        .collect::<Vec<_>>();
    let text = items.join("");

    Ok(text)
}
