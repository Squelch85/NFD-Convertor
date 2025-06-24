# NFD-Convertor

## English

iOS can store Hangul filenames in NFD form. For example `한글.txt` may appear
as `ㅎㅏㄴㄱㅡㄹ.txt`. This tool converts such names to the standard NFC form.

### Quick start
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Launch the GUI and drag files or folders:
   ```bash
   python NFD_Convertor.py
   ```
3. Or run on the command line:
   ```bash
   python NFD_Convertor.py --cli /path/to/item
   ```

## 한국어

iOS에서 파일 이름이 NFD 형식으로 저장될 수 있어 `한글.txt`가 `ㅎㅏㄴㄱㅡㄹ.txt`
처럼 보이기도 합니다. 이 도구를 사용하면 손쉽게 NFC 형식으로 변환할 수
있습니다.

### 빠른 시작
1. 의존성 설치
   ```bash
   pip install -r requirements.txt
   ```
2. GUI 실행 후 파일이나 폴더를 드래그합니다.
   ```bash
   python NFD_Convertor.py
   ```
3. 또는 명령행에서 실행합니다.
   ```bash
   python NFD_Convertor.py --cli 경로
   ```
