# Lumos
Lumos is a tool for analysis of postprocessing data of cardiovascular magnetic resonance imaging (CMR). A user interface is available for improved usability, the code of the backend is provided for coders.
Lumos enables the comparison of multiple readers and was especially developed to compare scar quantification methods on Late Gadolinium Enhancement (LGE) images but can be extended to additional uses.  

# Dependencies
Python 3.12 or newer is required. We recommend a separate environment for using this software. Further information and dependencies/libraries can be seen in the setup.cfg.   

# First Use
For a detailed overview of the software and possible applications see our paper. As an examplary application and a first user experience the EMIDEC data can be used.
1.	Install Repository
      * Clone the repository
      * Navigate to it
      * Install Lumos with dependicies by using: ` pip install -e . `
2.	Install Mongo DB
3.  Use the EMIDEC Data as first application case:
      *  Download EMIDEC Data by following the guide on ([EMIDEC website](https://emidec.com/dataset)).
      *  Zipped annotations for a first application case are automatically downloaded with Lumos in /docs.
      *	 Use Notebook 'Emidec_Converter' to convert Emidec Data into dicom format
      *	 Use Notebook 'MongoDB_Manager' to import dicoms and annotations into MongoDB and create necessary class structure
4.	Open Lumos’ User Interface: 
      * Open terminal
      * Activate environment
      * Navigate to Lumos/src
      * Use: `python` and `from Lumos.Guis import Multi_Reader_Comparison_Tool as _; _.main()`
5.  Use Lumos to analyze and compare readers: 
      *	Main Tab shows reader selection and cases list
      *	Overview tab shows selected readers
        +	Select image type ‘LGE SAX’
        +	Open either statistics tab or case tabs (Annotational comparison or histograms)
        +	For more info on Lumos' capabilities see our paper provided supplementary material.



# Disclaimer
Lumos is not a licensed medical product, but intended as a research tool to aid in the quality assurance of CMR postprocessing.

# Licence
If the code was helpful to you, please cite our paper.  link

