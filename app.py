import streamlit as st
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

st.title("RSA Signature Demo")

if 'key_size' not in st.session_state:
    st.session_state.key_size = 2048  # default value or any value you want
    st.session_state.private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=st.session_state.key_size,
        backend=default_backend()
    )

key_size_temp = st.radio("Generate RSA Key Size", [512, 1024, 2048, 4096], index=[512, 1024, 2048, 4096].index(st.session_state.key_size))

if key_size_temp != st.session_state.key_size:
    st.session_state.key_size = key_size_temp
    st.session_state.private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=st.session_state.key_size,
        backend=default_backend()
    )
    if "provide_signature" in st.session_state:
        del st.session_state["provide_signature"]
    if "file_bytes" in st.session_state:
        del st.session_state["file_bytes"]

private_key = st.session_state.private_key
public_key = private_key.public_key()

private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
).decode("utf-8")

public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
).decode("utf-8")

cols = st.columns(2)
with cols[0]:
    st.text_area("Public Key", public_pem, height=500)
    st.download_button("Download Public Key", public_pem, file_name="public_key.pem")
with cols[1]:
    st.text_area("Private Key", private_pem, height=500)
    st.download_button("Download Private Key", private_pem, file_name="private_key.pem")

option = st.radio("Choose Functionality", ["Generate Signature", "Verify Signature"])

hash_func = st.selectbox("Choose hash function:", ["SHA1", "MD5"])
hash_choice = {"SHA1": hashes.SHA1(), "MD5": hashes.MD5()}[hash_func]

def is_valid_hex(s):
    try:
        bytes.fromhex(s)
        return True
    except ValueError:
        return False


if option == "Generate Signature":
    uploaded_file = st.file_uploader("Choose a file to sign")

    if uploaded_file:
        st.session_state.file_bytes = uploaded_file.read()
        
        signature = private_key.sign(
            st.session_state.file_bytes,
            padding.PSS(
                mgf=padding.MGF1(hash_choice),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hash_choice
        )
        st.text_area("Signature Output (hex)", signature.hex(), height=250)
        st.session_state.provide_signature = signature.hex()
        st.download_button("Download Signature", signature.hex(), file_name="signature.txt")

elif option == "Verify Signature":
    if "provide_signature" in st.session_state:
        st.text_area("Provide Signature Value", st.session_state.provide_signature, height=250)
    else:
        st.warning("Please generate a signature first!")

    uploaded_signature_file = st.file_uploader("Upload a signature file")
    
    if uploaded_signature_file:
        uploaded_signature = uploaded_signature_file.read().decode("utf-8")
        st.session_state.uploaded_signature = uploaded_signature
    else:
        uploaded_signature = st.session_state.get("uploaded_signature", "")
    
    if st.button("Verify Signature"):
        if uploaded_signature and "file_bytes" in st.session_state:
            if is_valid_hex(uploaded_signature):
                signature_bytes = bytes.fromhex(uploaded_signature)
                try:
                    public_key.verify(
                        signature_bytes,
                        st.session_state.file_bytes,
                        padding.PSS(
                            mgf=padding.MGF1(hash_choice),
                            salt_length=padding.PSS.MAX_LENGTH
                        ),
                        hash_choice
                    )
                    st.success("Signature is valid!")
                except:
                    st.error("Signature is not valid!")
            else:
                st.error("Signature is not valid!")
