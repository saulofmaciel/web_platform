from spire.pdf.common import *
from spire.pdf import *

# Create a PdfDocument object
doc = PdfDocument()

# Load a PDF file
doc.LoadFromFile("C:\\PythonProjects\\project_33\\web_platform\\media\\certificates\\declaracao_INSS.pdf")

# Specify the path of the pfx certificate
pfxCertificatePath = "C:\\PythonProjects\\project_33\\web_platform\\staticfiles\\23996454_out.pfx"

# Specify the password of the pdf certificate
pfxPassword = "mitu$2024"

# Create a signature maker
signatureMaker = PdfOrdinarySignatureMaker(doc, pfxCertificatePath , pfxPassword)

# Get the signature
signature = signatureMaker.Signature

# Configure the signature properties like the signer's name, contact information, location and reason
signature.Name = "Alexander"
signature.ContactInfo = "555666"
signature.Location = "U.S."
signature.Reason = "This is the final version."

# Create a signature appearance
appearance = PdfSignatureAppearance(signature)

# Set labels for the signature
appearance.NameLabel = "Signer: "
appearance.ContactInfoLabel = "Phone: "
appearance.LocationLabel = "Location: "
appearance.ReasonLabel = "Reason: "

# Set the graphic mode as SignDetail
appearance.GraphicMode = GraphicMode.SignDetail

# Get the last page
page = doc.Pages[doc.Pages.Count - 1]

# Add the signature to a specified location of the page
signatureMaker.MakeSignature("Signature by God", page, 54.0, page.Size.Height - 100.0, 150.0, 50.0, appearance)

# Save the signed document
doc.SaveToFile("SignWithText.pdf")

# Dispose resources
doc.Dispose()