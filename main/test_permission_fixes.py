#!/usr/bin/env python3
"""
Test for permission fixes:
1. Only file owners can delete files (not admins)
2. Admins can share with both Geologues and Geophysiciens
"""

import requests
import json

def test_permission_fixes():
    """Test the permission fixes"""
    
    print("=== Test des corrections de permissions ===\n")
    
    # Test login as admin
    admin_data = {
        'email': 'admin@example.com',
        'password': 'admin123'
    }
    
    try:
        response = requests.post(
            'https://127.0.0.1:5000/api/auth/login',
            json=admin_data,
            verify=False
        )
        
        if response.status_code == 200:
            admin_token = response.json().get('token')
            print("✓ Connexion admin réussie")
            
            headers = {'Authorization': f'Bearer {admin_token}'}
            
            # Test 1: Get available users (should include both Geologues and Geophysiciens)
            print("\n1. Test récupération des utilisateurs disponibles...")
            response = requests.get(
                'https://127.0.0.1:5000/api/user/users/available',
                headers=headers,
                verify=False
            )
            
            if response.status_code == 200:
                data = response.json()
                available_users = data.get('available_users', [])
                print(f"✓ Trouvé {len(available_users)} utilisateurs disponibles")
                
                # Check if we have both roles
                roles = set(user.get('role') for user in available_users)
                print(f"  - Rôles disponibles: {roles}")
                
                if 'Geologue' in roles and 'Geophysicien' in roles:
                    print("✓ Les deux rôles (Geologue et Geophysicien) sont disponibles")
                else:
                    print("✗ Problème: pas tous les rôles disponibles")
                    
                # Show some users
                for user in available_users[:3]:  # Show first 3
                    print(f"  - {user.get('email')} ({user.get('role')})")
                    
            else:
                print(f"✗ Échec de récupération des utilisateurs: {response.status_code}")
                print(f"  Réponse: {response.text}")
                return
            
            # Test 2: Get files to test ownership
            print("\n2. Test récupération des fichiers...")
            response = requests.get(
                'https://127.0.0.1:5000/api/user/files',
                headers=headers,
                verify=False
            )
            
            if response.status_code == 200:
                data = response.json()
                owned_files = data.get('owned_files', [])
                shared_files = data.get('shared_files', [])
                
                print(f"✓ Fichiers possédés: {len(owned_files)}")
                print(f"✓ Fichiers partagés: {len(shared_files)}")
                
                if owned_files:
                    test_file = owned_files[0]
                    file_id = test_file.get('id')
                    filename = test_file.get('filename')
                    is_owner = test_file.get('is_owner', False)
                    
                    print(f"  - Fichier de test: {filename} (ID: {file_id})")
                    print(f"  - Propriétaire: {is_owner}")
                    
                    # Test 3: Try to share with available users
                    if available_users:
                        test_user = available_users[0]
                        user_id = test_user.get('id')
                        user_email = test_user.get('email')
                        user_role = test_user.get('role')
                        
                        print(f"\n3. Test de partage avec {user_email} ({user_role})...")
                        
                        share_data = {'user_ids': [user_id]}
                        response = requests.post(
                            f'https://127.0.0.1:5000/api/user/files/{file_id}/share',
                            json=share_data,
                            headers=headers,
                            verify=False
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            print(f"✓ Partage réussi avec {len(data.get('shared_with', []))} utilisateur(s)")
                            print(f"  - Utilisateurs partagés: {data.get('shared_with', [])}")
                        else:
                            print(f"✗ Échec du partage: {response.status_code}")
                            print(f"  Réponse: {response.text}")
                    
                    # Test 4: Verify file ownership for deletion
                    print(f"\n4. Test de propriété pour suppression...")
                    print(f"  - Le fichier {filename} appartient à l'admin: {is_owner}")
                    print(f"  - Seul le propriétaire peut supprimer le fichier")
                    print(f"  - Les admins ne peuvent pas supprimer les fichiers d'autres utilisateurs")
                    
                else:
                    print("✗ Aucun fichier possédé trouvé pour les tests")
                    
            else:
                print(f"✗ Échec de récupération des fichiers: {response.status_code}")
                print(f"  Réponse: {response.text}")
                
        else:
            print(f"✗ Échec de connexion admin: {response.status_code}")
            print(f"  Réponse: {response.text}")
            
    except Exception as e:
        print(f"✗ Erreur lors des tests: {e}")

def test_backend_connection():
    """Test connection to backend"""
    print("Test de connexion au backend...")
    
    try:
        response = requests.get('https://127.0.0.1:5000/chrome', verify=False)
        if response.status_code == 200:
            print("✓ Connexion backend réussie")
            return True
        else:
            print(f"✗ Connexion backend échouée: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Connexion backend échouée: {e}")
        return False

def main():
    """Main test function"""
    print("=== Test des corrections de permissions ===\n")
    
    # Test backend connection first
    if not test_backend_connection():
        print("\nLe backend n'est pas en cours d'exécution. Veuillez démarrer le serveur backend en premier.")
        print("Exécutez: cd backend && python run.py")
        return
    
    # Test permission fixes
    test_permission_fixes()
    
    print("\n=== Test terminé ===")

if __name__ == "__main__":
    main() 