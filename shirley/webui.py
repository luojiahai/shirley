import gradio as gr
import shirley as sh


def main() -> None:
    avatar_images=(
        sh.utils.getpath('./static/images/grinning-face.png'),
        sh.utils.getpath('./static/images/shark.png'),
    )

    with gr.Blocks(
        theme=gr.themes.Default(
            primary_hue=gr.themes.colors.cyan,
            secondary_hue=gr.themes.colors.sky,
            radius_size=gr.themes.sizes.radius_none,
        ),
        title='Shirley WebUI',
        css=sh.utils.getpath('./static/css/custom.css'),
    ) as blocks:
        sh.interfaces.Header()
        with gr.Tab('✨ Chat (聊天/唠嗑)'):
            sh.interfaces.Chat(avatar_images=avatar_images)
        with gr.Tab('💬 Text-To-Speech (文字转语音)'):
            sh.interfaces.TextToSpeech()
        sh.interfaces.Footer()

    blocks.queue().launch(
        server_name='127.0.0.1',
        server_port=8000,
        favicon_path=sh.utils.getpath('./static/favicon.ico'),
        show_api=False,
    )


if __name__ == '__main__':
    main()
