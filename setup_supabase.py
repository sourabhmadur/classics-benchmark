#!/usr/bin/env python3
"""
Guided Supabase setup script for CLASSICS-EMR.

This script helps you set up Supabase for the CLASSICS-EMR benchmark by:
1. Checking if Supabase is installed
2. Guiding you through project creation
3. Setting environment variables
4. Creating database tables
5. Testing the setup

Run this script to get started with Supabase.
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"🔧 {title}")
    print("=" * 60)

def print_step(step_num, title):
    """Print a formatted step header."""
    print(f"\n📋 Step {step_num}: {title}")
    print("-" * 40)

def check_supabase_package():
    """Check if Supabase package is installed."""
    print_step(1, "Checking Supabase Package")
    
    try:
        import supabase
        print("✅ Supabase package is installed")
        return True
    except ImportError:
        print("❌ Supabase package not found")
        print("\n💡 Installing Supabase package...")
        
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "supabase>=2.0.0"], 
                         check=True, capture_output=True)
            print("✅ Supabase package installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install Supabase: {e}")
            print("💡 Try running: pip install supabase>=2.0.0")
            return False

def guide_project_creation():
    """Guide user through Supabase project creation."""
    print_step(2, "Supabase Project Setup")
    
    print("🌐 Create a new Supabase project:")
    print("   1. Go to https://supabase.com")
    print("   2. Sign up/login")
    print("   3. Click 'New Project'")
    print("   4. Choose your organization")
    print("   5. Fill in project details:")
    print("      - Name: classics-emr (or any name)")
    print("      - Database Password: (create a strong password)")
    print("      - Region: (choose closest to you)")
    print("   6. Click 'Create new project'")
    print("   7. Wait 1-2 minutes for setup to complete")
    
    input("\n⏳ Press Enter when your project is ready...")

def get_credentials():
    """Guide user through getting credentials."""
    print_step(3, "Getting Project Credentials")
    
    print("🔑 Get your project credentials:")
    print("   1. In your Supabase dashboard, go to Settings → API")
    print("   2. Copy the following values:")
    print("      - Project URL (under 'Project URL')")
    print("      - anon/public key (under 'Project API keys')")
    
    print("\n📋 Enter your credentials:")
    
    url = input("🌐 Project URL: ").strip()
    while not url.startswith('https://') or not url.endswith('.supabase.co'):
        print("❌ Invalid URL format. Should be: https://your-project-id.supabase.co")
        url = input("🌐 Project URL: ").strip()
    
    key = input("🔑 Anon Key: ").strip()
    while len(key) < 100:  # Supabase keys are long
        print("❌ Invalid key format. Should be a long string (~100+ characters)")
        key = input("🔑 Anon Key: ").strip()
    
    return url, key

def set_environment_variables(url, key):
    """Set environment variables."""
    print_step(4, "Setting Environment Variables")
    
    # Determine shell type
    shell = os.environ.get('SHELL', '/bin/bash')
    if 'zsh' in shell:
        rc_file = Path.home() / '.zshrc'
    else:
        rc_file = Path.home() / '.bashrc'
    
    print(f"📝 Adding environment variables to {rc_file}")
    
    # Check if variables already exist
    env_lines = [
        f'export SUPABASE_URL="{url}"',
        f'export SUPABASE_ANON_KEY="{key}"'
    ]
    
    try:
        if rc_file.exists():
            with open(rc_file, 'r') as f:
                content = f.read()
        else:
            content = ""
            
        # Remove existing SUPABASE variables
        lines = content.split('\n')
        new_lines = [line for line in lines if not line.startswith('export SUPABASE_')]
        
        # Add new variables
        new_lines.extend(env_lines)
        
        # Write back
        with open(rc_file, 'w') as f:
            f.write('\n'.join(new_lines) + '\n')
            
        print(f"✅ Environment variables added to {rc_file}")
        
        # Set for current session
        os.environ['SUPABASE_URL'] = url
        os.environ['SUPABASE_ANON_KEY'] = key
        
        print("✅ Environment variables set for current session")
        print(f"💡 Run 'source {rc_file}' or restart your terminal to use in other sessions")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to set environment variables: {e}")
        print("💡 Manually add these lines to your shell config:")
        for line in env_lines:
            print(f"   {line}")
        return False

def create_database_tables():
    """Guide user through database table creation."""
    print_step(5, "Creating Database Tables")
    
    print("🗄️  Create database tables:")
    print("   1. In your Supabase dashboard, go to SQL Editor")
    print("   2. Click 'New query'")
    print("   3. Copy and paste the SQL from docs/supabase_setup_guide.md")
    print("   4. Or copy the SQL from the section below:")
    
    print("\n" + "─" * 60)
    print("SQL CODE TO COPY:")
    print("─" * 60)
    
    sql_file = Path("docs/supabase_setup_guide.md")
    if sql_file.exists():
        with open(sql_file, 'r') as f:
            content = f.read()
            # Extract SQL from the guide
            if '```sql' in content:
                sql_start = content.find('```sql') + 6
                sql_end = content.find('```', sql_start)
                sql_code = content[sql_start:sql_end].strip()
                print(sql_code)
            else:
                print("❌ Could not extract SQL from setup guide")
                print("💡 Check docs/supabase_setup_guide.md for the SQL code")
    else:
        print("❌ Setup guide not found")
        print("💡 Check docs/supabase_setup_guide.md for the SQL code")
    
    print("─" * 60)
    print("   5. Click 'Run' to execute the SQL")
    print("   6. Verify that the tables were created successfully")
    
    input("\n⏳ Press Enter when you've created the tables...")

def test_setup():
    """Test the complete setup."""
    print_step(6, "Testing Setup")
    
    print("🧪 Running setup tests...")
    
    try:
        # Run the test script
        result = subprocess.run([sys.executable, "test_supabase_setup.py"], 
                              capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
            
        if result.returncode == 0:
            print("🎉 All tests passed! Supabase setup is complete.")
            return True
        else:
            print("❌ Some tests failed. Check the output above.")
            return False
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def main():
    """Main setup flow."""
    print_header("CLASSICS-EMR Supabase Setup")
    
    print("This script will guide you through setting up Supabase for the CLASSICS-EMR benchmark.")
    print("You'll need:")
    print("  - A free Supabase account")
    print("  - Internet connection")
    print("  - About 5-10 minutes")
    
    if input("\n🚀 Ready to start? (y/n): ").lower() != 'y':
        print("👋 Setup cancelled. Run this script again when ready.")
        return
    
    # Step 1: Check Supabase package
    if not check_supabase_package():
        print("❌ Cannot proceed without Supabase package")
        return
    
    # Step 2: Guide project creation
    guide_project_creation()
    
    # Step 3: Get credentials
    url, key = get_credentials()
    
    # Step 4: Set environment variables
    if not set_environment_variables(url, key):
        print("⚠️  Environment variables not set automatically")
        print("💡 Set them manually before proceeding")
    
    # Step 5: Create database tables
    create_database_tables()
    
    # Step 6: Test setup
    if test_setup():
        print_header("Setup Complete! 🎉")
        print("✅ Supabase is now configured for CLASSICS-EMR")
        print("💡 You can now run experiments and results will be logged to your database")
        print("📊 View results in your Supabase dashboard → Table Editor")
        print("\n🔗 Useful commands:")
        print("  - python test_supabase_setup.py  # Test setup again")
        print("  - Check your environment: echo $SUPABASE_URL")
    else:
        print_header("Setup Incomplete ⚠️")
        print("❌ Please fix the issues above and run the test script again:")
        print("   python test_supabase_setup.py")

if __name__ == "__main__":
    main() 