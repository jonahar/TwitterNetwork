import java.io.File;
import java.io.IOException;


import org.gephi.graph.api.DirectedGraph;
import org.gephi.graph.api.GraphController;
import org.gephi.graph.api.GraphModel;
import org.gephi.io.importer.api.Container;
import org.gephi.io.importer.api.EdgeDirectionDefault;
import org.gephi.io.importer.api.ImportController;
import org.gephi.io.processor.plugin.DefaultProcessor;
import org.gephi.layout.plugin.forceAtlas2.ForceAtlas2;
import org.gephi.project.api.ProjectController;
import org.gephi.project.api.Workspace;
import org.gephi.statistics.plugin.Modularity;
import org.openide.util.Lookup;
import org.gephi.layout.plugin.forceAtlas2.ForceAtlas2Builder;
import org.gephi.statistics.plugin.PageRank;


public class CreateGraphs
{
    // this program loads multiple .gexf files into one .gephi file (each gexf in different workspace).
    // Compute modularity+PageRank and run forceAtlas for each graph.


    public static void main(String[] args)
    {
        String[] graphFilepaths = {"gexf/all.gexf", "gexf/retweet.gexf", "gexf/quote.gexf", "gexf/reply.gexf", "gexf/like.gexf"};
        String[] graphNames = {"all", "retweet", "quote", "reply", "like"};
        makeAllGraphs(graphFilepaths, graphNames);
    }

    static void makeAllGraphs(String[] graphFilepaths, String[] graphNames)
    {

        try
        {
            ProjectController pc = (ProjectController) Lookup.getDefault().lookup(ProjectController.class);
            pc.newProject();

            // load each gexf file to a new workspace and run all operations on it
            for (int i = 0; i < graphFilepaths.length; i++)
            {
                Workspace workspace = pc.newWorkspace(pc.getCurrentProject());
                pc.renameWorkspace(workspace, graphNames[i]);
                script(graphFilepaths[i], workspace, 400);
            }
            saveProject(pc, "graphs.gephi");

        }
        catch (Exception e)
        {
            e.printStackTrace();
        }
    }


    /**
     * @param graphFilepath graph description file to load
     * @param workspace     the workspace to work in
     * @param iter          number of iterations for ForceAtlas2
     * @throws IOException
     */
    static void script(String graphFilepath, Workspace workspace, int iter) throws IOException
    {

        //Get controllers and models
        ImportController importController = (ImportController) Lookup.getDefault().lookup(ImportController.class);
        GraphModel graphModel = ((GraphController) Lookup.getDefault().lookup(GraphController.class)).getGraphModel(workspace);

        //Import file
        Container container;
        File file = new File(graphFilepath);
        container = importController.importFile(file);
        container.getLoader().setEdgeDefault(EdgeDirectionDefault.DIRECTED);   //Force DIRECTED

        //Append imported data to GraphAPI
        importController.process(container, new DefaultProcessor(), workspace);

        //See if graph is well imported
        DirectedGraph graph = graphModel.getDirectedGraph();
        //System.out.println("Nodes: " + graph.getNodeCount());
        //System.out.println("Edges: " + graph.getEdgeCount());

        // Run modularity algorithm - community detection
        runModularity(graphModel, workspace);

        // Run PageRank
        runPageRank(graphModel, workspace);

        // Run ForceAtlas2
        runForceAtlas2(graphModel, iter);
    }


    static void runPageRank(GraphModel graphModel, Workspace workspace)
    {
        System.out.print("Running PageRank... ");
        PageRank pageRank = new PageRank();
        pageRank.setDirected(true);
        pageRank.execute(graphModel);
        System.out.println("Done");
    }


    /**
     * Run the modularity algorithm and set nodes colors according to the communities found.
     *
     * @param graphModel
     */
    static void runModularity(GraphModel graphModel, Workspace workspace)
    {
        System.out.print("Running modularity... ");
        Modularity modularity = new Modularity();
        modularity.execute(graphModel);
        System.out.println("Done");
    }


    static void runForceAtlas2(GraphModel model, int iter)
    {
        System.out.println("Running ForceAtlas2");
        ForceAtlas2 fa2 = new ForceAtlas2Builder().buildLayout();
        fa2.setGraphModel(model);
        fa2.resetPropertiesValues();

        fa2.initAlgo();
        for (int i = 0; i < iter && fa2.canAlgo(); i++)
        {
            if ((i + 1) % 100 == 0)
            {
                System.out.print(i + 1);
                System.out.println(" iterations done");
            }
            fa2.goAlgo();
        }
        fa2.endAlgo();
    }

    static void saveProject(ProjectController pc, String outputFilepath)
    {
        File file = new File(outputFilepath);
        pc.saveProject(pc.getCurrentProject(), file).run();
    }
}
