# Lumos
Lumos is a tool for analysis of postprocessing data of cardiovascular magnetic resonance imaging (CMR). A user interface is available for improved usability, the code of the backend is provided for coders.
Lumos enables the comparison of multiple readers and was especially developed to compare scar quantification methods on Late Gadolinium Enhancement (LGE) images but can be extended to additional uses.  

# Dependencies
Python 3.12 or newer is required. We recommend a separate environment for using this software. Further information and dependencies/libraries can be seen in the setup.cfg.   

# Installation and First Use
For a detailed overview of the software and possible applications see our paper. As an examplary application and a first user experience the EMIDEC data can be used.
1.	Install Repository
      * Clone the repository
      * Navigate to it
      * Install Lumos with dependicies by using: ` pip install -e . `
2.	Install Mongo DB
      * Install [MongoDB Community](https://www.mongodb.com/docs/manual/administration/install-community/)
      * Install [MongoDB Compass](https://www.mongodb.com/docs/compass/current/install/#std-label-download-install) as MongoDB User Interface
      * run MongoDB-community and connect to local server (localhost:27017)
3.  Use the EMIDEC Data as first application case:
      *  Download EMIDEC Data by following the guide on ([EMIDEC website](https://emidec.com/dataset)).
      *  Zipped additional annotations for a first application case on the EMIDEC images are automatically downloaded with Lumos in /docs.
      *	 Use Notebook 'Emidec_Converter' in Lumos/Notebooks to convert Emidec Data (Images) into dicom format
      *	 Use Notebook 'MongoDB_Manager' in Lumos/Notebooks to import dicoms and annotations into MongoDB and create necessary class structure. You need to adjust the paths in the notebook to where you stored images and annotations as explained in the Notebook. Lumos will then be able to utilize this MongoDB Database. You can see the database in the MongoDB Compass on the lefthandside below databases as 'Lumos_CMR_QualityAssuranceDatabase'.
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
If the code was helpful to you, please cite [our paper](https://link.springer.com/article/10.1007/s10278-025-01437-2).

