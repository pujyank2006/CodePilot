from app.services.repository_scanner import RepositoryScanner

scanner = RepositoryScanner()
files = scanner.scan(r"D:\FSD\Hyperlocal-Marketplace")

for file in files:
    print(file)