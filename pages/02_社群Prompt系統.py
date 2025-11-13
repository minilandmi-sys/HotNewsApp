import streamlit as st
import re
import json

# --- 1. 定義常數與預設數據 ---

# 預設的風格清單及其描述 (S1.1, S1.2)
STYLE_CONFIG = {
    "專業正式 (Professional)": {
        "description": "嚴謹、數據導向，適合商業報告、正式公告。",
        "prompt_prefix": "請以專業且正式的語氣，基於以下內容生成社群貼文。確保語法嚴謹，並在結尾加上相關數據或結論。",
    },
    "幽默活潑 (Casual & Lively)": {
        "description": "用語輕鬆、貼近年輕人，適合互動、娛樂內容。",
        "prompt_prefix": "請以幽默、活潑且具吸引力的語氣，改寫以下內容。多使用表情符號和網路流行語。",
    },
    "緊急促銷 (Urgent Promo)": {
        "description": "強調時效性、稀缺性，促使使用者立即行動 (CTA)。",
        "prompt_prefix": "請以緊急促銷的語氣生成貼文。必須包含強烈的行動呼籲 (CTA) 和截止日期。",
    },
    "教育分享 (Educational)": {
        "description": "清晰、步驟化、知識性，適合教學或深度解說。",
        "prompt_prefix": "請將以下內容整理為步驟清晰、易於理解的教育分享貼文。每個重點請使用條列式呈現。",
    },
}

# 預設模板 (T2.1, T2.2)
DEFAULT_TEMPLATES = {
    "活動宣傳基礎模板": """
🎉 重磅消息！我們的 [活動名稱] 活動即將開始！
日期：{{日期}}
地點：{{地點}}
主題：{{主題}}

詳細內容：
{{核心內容}}

趕快點擊 {{報名連結}} 了解更多資訊並報名參加吧！
#{{Hashtag1}} #{{Hashtag2}}
""",
    "產品發表模板": """
✨ 全新登場！隆重介紹我們的 {{產品名稱}}！
這款產品擁有以下突破性特色：
1. {{特色一}}
2. {{特色二}}

{{核心內容}}

立即體驗，享受 {{限時優惠}}！
👉 購買連結：{{購買連結}}
""",
}

# --- 2. Session State 初始化 (T2.1, T2.3) ---

def initialize_session_state():
    """初始化 Streamlit Session State，確保狀態持久化。"""
    if 'custom_templates' not in st.session_state:
        # 將預設模板載入到 Session State
        st.session_state.custom_templates = DEFAULT_TEMPLATES

    if 'selected_template_name' not in st.session_state:
        st.session_state.selected_template_name = list(DEFAULT_TEMPLATES.keys())[0]

# --- 3. 核心邏輯函式 ---

def extract_variables(template_text):
    """
    從模板文字中提取所有 {{...}} 變數 (A3.2, T2.4)。
    使用正則表達式尋找所有符合 {{變數名}} 格式的內容。
    """
    # 尋找所有被 {{ 和 }} 包裹的內容
    variables = re.findall(r"\{\{([^}]+)\}\}", template_text)
    # 移除重複的變數名並去除空白
    return sorted(list(set(v.strip() for v in variables)))

def generate_prompt(style_key, template_text, core_content, variable_values):
    """
    結合風格、模板、核心內容和變數，生成最終 Prompt (A3.3)。
    """
    # 1. 取得風格前綴 (指令)
    style_prefix = STYLE_CONFIG.get(style_key, {}).get("prompt_prefix", "")

    # 2. 替換模板中的變數
    processed_template = template_text
    for var, value in variable_values.items():
        placeholder = f"{{{{{var}}}}}"
        # 使用使用者輸入的值替換模板中的變數
        processed_template = processed_template.replace(placeholder, value)

    # 3. 組合最終 Prompt
    final_prompt = f"""
--- Prompt 指令 ---
{style_prefix}

--- 核心內容 ---
{core_content}

--- 套用模板後的貼文草稿 ---
{processed_template}
"""
    return final_prompt

# --- 4. 頁面 UI 佈局與事件處理 ---

def prompt_system_page():
    """Streamlit 頁面的主函式，包含 UI 和邏輯。"""
    
    # 標題應放在主內容區
    st.title("🤖 社群專用 Prompt 系統")
    st.markdown("---")

    initialize_session_state()
    
    # 初始化一個字典來存儲動態變數的值
    variable_values = {}

    # --- 左側欄/風格選擇與模板管理 (S1.1, T2.1, T2.3) ---
    # 所有側邊欄的內容都必須放在 with st.sidebar: 區塊內
    with st.sidebar:
        st.header("1️⃣ 選擇輸出風格")
        selected_style = st.selectbox(
            "請選擇您的 Prompt 風格：",
            list(STYLE_CONFIG.keys()),
            key='style_selector'
        )
        # 顯示風格描述 (S1.2)
        st.info(STYLE_CONFIG[selected_style]["description"])

        st.markdown("---")
        st.header("📝 模板管理 (T2.1, T2.3)")
        
        # 模板選擇器
        template_names = list(st.session_state.custom_templates.keys())
        # 使用 try-except 處理當模板剛被刪除，selected_template_name 尚未更新時可能出現的 KeyError
        try:
            default_index = template_names.index(st.session_state.selected_template_name)
        except ValueError:
             default_index = 0

        st.session_state.selected_template_name = st.selectbox(
            "載入已儲存模板：",
            template_names,
            index=default_index, # 確保預設選中正確的值
            key='template_loader'
        )
        
        # 取得當前選中的模板內容
        current_template = st.session_state.custom_templates.get(
            st.session_state.selected_template_name, 
            ""
        )
        
        # 模板編輯區 (T2.2)
        st.markdown("##### 編輯/新增模板內容")
        edited_template = st.text_area(
            "請使用 {{變數名}} 定義可替換的欄位：",
            value=current_template,
            height=200,
            key="template_editor"
        )
        
        # 儲存模板按鈕 (T2.3)
        st.markdown("---")
        template_name_input = st.text_input(
            "儲存為新模板名稱：", 
            value=st.session_state.selected_template_name,
            key='new_template_name'
        )
        
        col_save, col_delete = st.columns(2)
        with col_save:
            if st.button("💾 儲存/更新模板"):
                if template_name_input:
                    st.session_state.custom_templates[template_name_input] = edited_template
                    st.session_state.selected_template_name = template_name_input
                    st.success(f"模板已儲存為：『{template_name_input}』")
                    st.rerun() # 重新載入，更新模板選單
                else:
                    st.error("請輸入模板名稱！")
        
        with col_delete:
            # 只有當模板數量大於 1 時才允許刪除 (保留至少一個模板)
            if len(template_names) > 1 and st.button("🗑️ 刪除模板"):
                del st.session_state.custom_templates[st.session_state.selected_template_name]
                # 刪除後，選擇列表中的第一個模板作為新的預設值
                st.session_state.selected_template_name = list(st.session_state.custom_templates.keys())[0]
                st.warning(f"已刪除模板：『{st.session_state.selected_template_name}』")
                st.rerun()


    # --- 主內容區佈局 (使用兩欄) ---
    col1, col2 = st.columns(2)

    with col1:
        st.header("2️⃣ 內容輸入與變數填充")
        
        # 核心內容輸入區 (A3.1)
        st.subheader("核心內容輸入 (Prompt 的主要資訊)")
        core_content = st.text_area(
            "請在此輸入貼文、產品或活動的原始描述：",
            height=250,
            key="core_content_input",
            placeholder="例如：我們將在週六舉辦一場關於 AI 寫作技巧的免費線上講座，報名人數已達 80% 額滿！"
        )

        # 變數解析與填充 (A3.2)
        st.subheader("動態變數填充")
        
        # 取得編輯器中或已選模板中的變數
        template_to_parse = st.session_state.custom_templates.get(st.session_state.selected_template_name, edited_template)
        
        required_variables = extract_variables(template_to_parse)

        if required_variables:
            st.markdown("請填寫模板中的所有變數：")
            
            # 動態生成變數輸入框
            for var in required_variables:
                # 每個變數對應一個 text_input
                value = st.text_input(
                    f"**{var}**:", 
                    key=f"var_input_{var}",
                    placeholder=f"請輸入 {var} 的值"
                )
                variable_values[var] = value
        else:
            st.info("此模板中未偵測到任何變數 (e.g. {{日期}})。")
            
    with col2:
        st.header("3️⃣ 最終 Prompt 生成")
        
        # 處理模板變數替換
        all_variables_filled = all(variable_values.values()) or not required_variables
        
        if core_content and all_variables_filled:
            # 生成最終 Prompt
            final_prompt = generate_prompt(
                selected_style, 
                template_to_parse, 
                core_content, 
                variable_values
            )
            
            st.success("✅ Prompt 已生成！")
            
            # 最終 Prompt 顯示區 (A3.3)
            # 使用 st.code 讓使用者可以一鍵複製 (A3.4)
            st.code(final_prompt, language='markdown')
            
            st.markdown("""
            ---
            **使用說明：**
            1. 將上方 Prompt 完整複製到您慣用的 LLM (如 Gemini, ChatGPT) 中。
            2. LLM 將根據您的**風格指令**和**核心內容**，產出高品質的社群貼文。
            """)
            
        else:
            st.warning("請在左側填寫核心內容和所有動態變數後，才能生成 Prompt。")


# 確保此檔案作為 Streamlit 頁面執行
if __name__ == "__main__":
    prompt_system_page()
