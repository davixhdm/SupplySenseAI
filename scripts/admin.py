
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings

def main():
    while True:
        print("\n" + "=" * 50)
        print("  SupplySense AI — Admin CLI")
        print("=" * 50)
        print(f"\n  Engine Status: {'✅ Running' if settings.ENVIRONMENT == 'production' else '⚠️  Dev Mode'}")
        print(f"  Groq Key: {'✅ Configured' if settings.GROQ_API_KEY else '❌ Missing'}")
        print(f"  Admin Password: {'✅ Set' if settings.ADMIN_PASSWORD != 'admin123' else '⚠️  Default'}")
        print("\n  1. View config")
        print("  2. Test health endpoint")
        print("  3. Exit")
        
        choice = input("\n  Choose: ").strip()
        if choice == "1":
            print(f"\n  APP_NAME: {settings.APP_NAME}")
            print(f"  PORT: {settings.PORT}")
            print(f"  GROQ_KEY: {'***' + settings.GROQ_API_KEY[-4:] if settings.GROQ_API_KEY else 'Not set'}")
            print(f"  ADMIN_PASSWORD: {'***' if settings.ADMIN_PASSWORD else 'Not set'}")
        elif choice == "2":
            import httpx, asyncio
            async def test():
                async with httpx.AsyncClient() as c:
                    r = await c.get(f"http://localhost:{settings.PORT}/api/health")
                    print(f"\n  Response: {r.json()}")
            asyncio.run(test())
        elif choice == "3":
            print("\n  Goodbye.")
            break
        else:
            print("\n  Invalid choice.")
        input("\n  Press Enter...")

if __name__ == "__main__":
    main()