import gc
from bot_gadu import PDFProcessor

def main():
    gc.collect()
    botgadu = PDFProcessor()
    botgadu.run()

if __name__ == "__main__":
    main()
