from RoomOfRequirement.ClinicalResults import *
from RoomOfRequirement.Views.View import *

from RoomOfRequirement.Tables  import *
from RoomOfRequirement.Figures import *

import traceback

import csv
import PIL


class LAX_CINE_2CV_View(View):
    def __init__(self):
        self.name = 'LAX CINE 2CV'
        self.cmap = 'gray'
        self.contour_names = ['la'] #'lv_lax_endo', 'lv_lax_myo', 
        self.clinical_parameters = [cr() for cr in [LAX_2CV_LAESPHASE,  LAX_2CV_LAEDPHASE, LAX_2CV_LAESAREA, LAX_2CV_LAEDAREA]]
        self.clinical_parameters = {cr.name: cr for cr in self.clinical_parameters}
        # ,LAX_2CV_LVESPHASE,  LAX_2CV_LVEDPHASE, LAX_2CV_LVESV,      LAX_2CV_LVEDV]
        self.clinical_phases = {'la':  [LAX_2CV_LAESPHASE().name,  LAX_2CV_LAEDPHASE().name],
                                'all': [LAX_2CV_LAESPHASE().name,  LAX_2CV_LAEDPHASE().name]}
        
        
        # register tabs here:
        import RoomOfRequirement.Guis.Addable_Tabs.CC_Metrics_Tab          as tab1
        import RoomOfRequirement.Guis.Addable_Tabs.CCs_ClinicalResults_tab as tab2
        import RoomOfRequirement.Guis.Addable_Tabs.CC_Overview_Tab         as tab4
        
        self.case_tabs  = {'Metrics and Figure':          tab1.CC_Metrics_Tab, 
                           'Clinical Results and Images': tab4.CC_CRs_Images_Tab}
        self.stats_tabs = {'Clinical Results'  : tab2.CCs_ClinicalResults_Tab}

    
    def store_information(self, evals1, evals2, path, icon_path, storage_version=0):
        if storage_version >= 0:
            try:
                cr_table = CC_ClinicalResultsAveragesTable()
                cr_table.calculate(self, evals1, evals2)
                crtol_p = cr_table.store(os.path.join(path, 'clinical_parameters_overview.csv'))
            except Exception as e:
                print(traceback.print_exc())
            try:
                cr_table = CCs_ClinicalResultsTable()
                cr_table.calculate(self, evals1)
                cr_table.store(os.path.join(path, 'clinical_parameters_percase_reader1.csv'))
            except Exception as e: print(traceback.print_exc())
            try:
                cr_table = CCs_ClinicalResultsTable()
                cr_table.calculate(self, evals2)
                cr_table.store(os.path.join(path, 'clinical_parameters_percase_reader2.csv'))
            except Exception as e: print(traceback.print_exc())
            try:
                cr_table = CCs_ClinicalResultsTable()
                cr_table.calculate_diffs(self, evals1, evals2)
                cr_table.store(os.path.join(path, 'clinical_parameters_percase_diffs.csv'))
            except Exception as e: print(traceback.print_exc())
            try:
                cr_overview_figure = LAX2CV_BlandAltman()
                cr_overview_figure.visualize(self, evals1, evals2)
                cr_p = cr_overview_figure.store(path)
            except Exception as e:
                print(traceback.print_exc())
            try:
                metrics_table = LAX_CCs_MetricsTable()
                metrics_table.calculate(self, ccs)
                metrics_table.store(os.path.join(path, 'metrics_phase_slice_table.csv'))
            except Exception as e:
                print(traceback.print_exc())
            try:
                failed_segmentation_folder_path = os.path.join(path, 'Failed_Segmentations')
                if not os.path.exists(failed_segmentation_folder_path): os.mkdir(failed_segmentation_folder_path)
                """
                failed_annotation_comparison = Failed_Annotation_Comparison_Yielder()
                failed_annotation_comparison.set_values(self, ccs)
                failed_annotation_comparison.store(failed_segmentation_folder_path)
                """
            except Exception as e:
                print(traceback.print_exc())
        
        if storage_version >= 1:
            try:
                cr_overview_figure = LAX_Volumes_BlandAltman()
                cr_overview_figure.visualize(self, ccs)
                crvol_p = cr_overview_figure.store(path)
            except Exception as e:
                print(traceback.print_exc())
        
        pdf = PDF(orientation='P', unit='mm', format='A4')
        
        if storage_version>=0:
            try:
                pdf.add_page()
                pdf.prepare_pretty_format(icon_path)
                # CRs TABLE
                data = [l[1:] for l in csv.reader(open(os.path.join(path, 'clinical_parameters_overview.csv')), delimiter=';')]
                for i in range(len(data)):
                    for j in range(len(data[i])):
                        try:    data[i][j] = "{:10.2f}".format(float(data[i][j].replace(',','.')))
                        except: data[i][j] = data[i][j]
                pdf.set_title('Clinical Parameter Means and Tolerance Ranges')
                pdf.set_table(data[0:], x=15, y=30, col_widths=[40.0]+[30 for i in range(len(data[0])-2)]+[40.0])
                pdf.set_text("Table. 1 This table shows the clinical parameter names in the first column. The other columns show statistics concerning the parameters. The first and second readers' means (stds) are shown in the second and third column, respectively. The mean and std of the differences between both readers is presented in the fourth column. The mean difference of both readers ± 95% confidence intervals are shown in parentheses with ±tolerance ranges thereafter. This provides information on whether the 95% estimate of the mean difference between both readers is within an acceptable limit.", 10, 210)
            except: print(traceback.print_exc())

        print()
        print()
        print('Storage Version: ', storage_version)
        if storage_version>=0:
            try:
                pdf.add_page()
                pdf.prepare_pretty_format(icon_path)
                pdf.set_title('Atrial Area Differences')
                pdf.set_chart(cr_p, 20, 35, w=695/4, h=641/4)
                pdf.set_text('Fig. 1 Area Differences for LA & RA: The first row presents Bland-Altman plots for the 4CV RA areas in ES and ED. The second row shows BA plots for the 4CV LA areas. The third row shows 2CV LA areas. The last row contains Dice value boxplots per contour on the left and Hausdorff distance boxplots on the right. Legend: ES: End-systole, ED: End-diastole, CV: Chamber View, LA: Left Atrium, RA: Right Atrium, Dice: Dice similarity coefficient', 10, 242)
            except: print(traceback.print_exc())
        
        if storage_version>=1:
            try:
                pdf.add_page()
                pdf.prepare_pretty_format(icon_path)
                pdf.set_title('Atrial Volume Differences')
                pdf.set_chart(crvol_p, 20, 35, w=695/4, h=841/4)
                pdf.set_text('Fig. 3 Volume Differences for LA & RA: The first row presents Bland-Altman plots for the 4CV RA ESV and RA EDV. The second row shows BA plots for the 4CV LA ESV and EDV. The third row shows 2CV LA ESV and EDV. The last row contains Dice value boxplots per contour on the left and Hausdorff distance boxplots on the right. Legend: ESV: End-systolic volume, EDV: End-diastole volume, CV: Chamber View, LA: Left Atrium, RA: Right Atrium, Dice: Dice similarity coefficient', 10, 242)
            except: print(traceback.print_exc())
        
        # ADD the QUALITATIVE FIGURES
        try:
            overviewtab = findCCsOverviewTab()
            view_name = type(self).__name__.replace('_View','').replace('_',' ')
            if len(overviewtab.qualitative_figures[view_name])!=0:
                
                pdf.add_page()
                pdf.prepare_pretty_format(icon_path)
                pdf.set_title('Qualitative Figures added during Manual Inspection')
                pdf.set_text('The following PDF pages reference figures, which were manually selected by the investigor and added to this report manually. Every figure has a title and comments that the investigator typed for elaboration.', 10, 50, size=12)
                
                for addable in overviewtab.qualitative_figures[view_name]:
                    pdf.add_page()
                    pdf.prepare_pretty_format()
                    img = PIL.Image.open(addable[1])
                    scale = img.height / img.width
                    pdf.set_text('Title:    ' + addable[0], 10, 20, size=12)
                    pdf.set_chart(addable[1], 20, 35, w=695/4, h=695/4*scale)
                    pdf.set_text(addable[2], 10, 40 + 695/4*scale)
        
        except Exception as e:
            print(traceback.print_exc())
            pass
        
        pdf.set_author('Luna Lovegood')
        pdf.output(os.path.join(path, view_name+'_report.pdf'))
        